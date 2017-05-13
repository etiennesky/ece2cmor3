import logging
import threading
import re
import Queue
import os
import cdoapi
import cmor_source
import cmor_target

# Log object
log = logging.getLogger(__name__)

# Threading parameters
task_threads = 1
cdo_threads = 4

# Flags to control whether to execute cdo.
skip = 1
append = 2
recreate = 3
modes = [skip,append,recreate]

# Mode for post-processing
mode = 3

# Output frequency of IFS (in hours)
output_frequency_ = 3

# Helper list of tasks
finished_tasks_ = []


# Post-processes a list of tasks
def post_process(tasks,path,max_size_gb = float("inf"),griddes = {}):
    global finished_tasks_,task_threads
    comdict = {}
    commbuf = {}
    max_size = 1000000000.*max_size_gb
    for task in tasks:
        command = create_command(task,griddes)
        commstr = command.create_command()
        if(commstr not in commbuf):
            commbuf[commstr] = command
        else:
            command = commbuf[commstr]
        if(command in comdict):
            comdict[command].append(task)
        else:
            comdict[command] = [task]
    invalid_commands = []
    for comm,tasklist in comdict.iteritems():
        if(not validate_tasklist(tasklist)):
            invalid_commands.append(comm)
    for comm in invalid_commands:
        comdict.pop(comm)
    finished_tasks_ = []
    if(task_threads <= 2):
        tmpsize = 0.
        for comm,tasklist in comdict.iteritems():
            if(tmpsize >= max_size):
                break
            f = apply_command(comm, tasklist,path)
            if(os.path.exists(f)): tmpsize += float(os.path.getsize(f))
            finished_tasks_.extend(tasklist)
    else:
        q = Queue.Queue()
        for i in range(task_threads):
            worker = threading.Thread(target = cdo_worker,args = (q,path,max_size))
            worker.setDaemon(True)
            worker.start()
        for (comm,tasklist) in comdict.iteritems():
            q.put((comm,tasklist))
        q.join()
    return list(finished_tasks_)



# Checks whether the task grouping makes sense: only tasks for the same variable and frequency can be safely grouped.
def validate_tasklist(tasks):
    global log
    freqset = set(map(lambda t:t.target.frequency,tasks))
    if(len(freqset) != 1):
        log.error("Multiple target variables joined to single cdo command: %s" % str(freqset))
        return False
    return True


# Creates a cdo postprocessing command for the given IFS task.
def create_command(task,griddes = {}):
    if(not isinstance(task.source,cmor_source.ifs_source)):
        raise Exception("This function can only be used to create cdo commands for IFS tasks")
    if(hasattr(task,"paths") and len(getattr(task,"paths")) > 1):
        raise Exception("Multiple merged cdo commands are not supported yet")
    result = cdoapi.cdo_command() if hasattr(task.source,cmor_source.expression_key) else cdoapi.cdo_command(code = task.source.get_grib_code().var_id)
    add_grid_operators(result,task,griddes)
    add_expr_operators(result,task)
    add_time_operators(result,task)
    add_level_operators(result,task)
    return result


# Checks whether the string expression denotes height level merging
def add_expr_operators(cdo,task):
    expr = getattr(task.source,cmor_source.expression_key,None)
    if(not expr): return
    sides = expr.split('=')
    if(len(sides)!=2):
        log.error("Could not parse expression %s" % expr)
        return
    regex = "var[0-9]{1,3}"
    if(not re.match(regex,sides[0])):
        log.error("Could not parse expression %s" % expr)
        return
    newcode = int(sides[0].strip()[3:])
    if(sides[1].startswith("merge(") and sides[1].endswith(")")):
        arg = sides[1][6:-1]
        subexprlist = arg.split(',')
        if(not any(getattr(task.target,"z_dims",[]))):
            log.warning("Encountered 3d expression for variable with no z-axis: taking first field")
            subexpr = subexprlist[0].strip()
            if(not re.match(regex,subexpr)):
                cdo.add_operator(cdoapi.cdo_command.expression_operator,"var" + str(newcode) + "=" + subexpr)
            else:
                task.source = cmor_source.ifs_source.read(subexpr)
            root_codes = [int(s.strip()[3:]) for s in re.findall(regex,subexpr)]
            cdo.add_operator(cdoapi.cdo_command.select_code_operator,*root_codes)
            return
        else:
            for subexpr in subexprlist:
                if(not re.match(regex,subexpr)):
                    subvars = re.findall(regex,subexpr)
                    if(len(subvars) != 1):
                        log.error("Merging expressions of multiple variables per layer is not supported.")
                        continue
                    cdo.add_operator(cdoapi.cdo_command.add_expression_operator,subvars[0] + "=" + subexpr)
            cdo.add_operator(cdoapi.cdo_command.set_code_operator,newcode)
    else:
        cdo.add_operator(cdoapi.cdo_command.expression_operator,expr)
    cdo.add_operator(cdoapi.cdo_command.select_code_operator,*[c.var_id for c in task.source.get_root_codes()])


# Multi-thread function wrapper.
def cdo_worker(q,basepath,maxsize):
    global finished_tasks_
    while(True):
        args = q.get()
        files = list(set(map(lambda t:getattr(t,"path",None),finished_tasks_)))
        if(sum(map(lambda f:os.path.getsize(f),[f for f in files if os.path.exists(f)])) < maxsize):
            tasks = args[1]
            apply_command(command = args[0],tasklist = tasks,basepath = basepath)
            finished_tasks_.extend(tasks)
        q.task_done()


# Executes the command (first item of tup), and replaces the path attribute for all tasks in the tasklist (2nd item of tup)
# to the output of cdo. This path is constructed from the basepath and the first task.
def apply_command(command,tasklist,basepath = None):
    global log,cdo_threads,skip,append,recreate,mode
    if(not tasklist):
        log.warning("Encountered empty task list for post-processing command %s" % command.create_command())
    if(basepath == None and mode in [skip,append]):
        log.warning("Executing post-processing in skip/append mode without directory given: this will skip the entire task.")
    ifile = getattr(tasklist[0],"path")
    ofname = tasklist[0].target.variable + "_" + tasklist[0].target.table + ".nc"
    ofile = os.path.join(basepath,ofname) if basepath else None
    for task in tasklist:
        commstr = command.create_command()
        log.info("Post-processing target %s in table %s from file %s with cdo command %s" % (task.target.variable,task.target.table,ifile,commstr))
        setattr(task,"cdo_command",commstr)
    result = ofile
    if(mode != skip):
        if(mode == recreate or (mode == append and not os.path.exists(ofile))):
            mergeexpr = (cdoapi.cdo_command.set_code_operator in command.operators)
            opath = command.apply(ifile,ofile,cdo_threads,grib_first = mergeexpr)
            if(opath and not basepath):
                tmppath = os.path.dirname(opath)
                ofile = os.path.join(tmppath,ofname)
                os.rename(opath,ofile)
                result = ofile
    for task in tasklist:
        setattr(task,"path",result)
    return result


# Adds grid remapping operators to the cdo commands for the given task
def add_grid_operators(cdo,task,griddes):
    grid = task.source.grid_id()
    if(grid == cmor_source.ifs_grid.spec):
        cdo.add_operator(cdoapi.cdo_command.spectral_operator)
    else:
        gridtype = griddes.get("gridtype","gaussian reduced")
        if(gridtype == "gaussian reduced"):
            cdo.add_operator(cdoapi.cdo_command.gridtype_operator,cdoapi.cdo_command.regular_grid_type)


# Adds time averaging operators to the cdo command for the given task
def add_time_operators(cdo,task):
    global output_frequency_
    freq = getattr(task.target,cmor_target.freq_key,None)
    operators = getattr(task.target,"time_operator",["point"])
    mon = int(getattr(task,"path","-1")[-2:])
    timeshift = "-" + str(output_frequency_) + "hours"
    if(freq == "mon"):
        if(operators == ["point"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,12)
            cdo.add_operator(cdoapi.cdo_command.select_day_operator,15)
        elif(operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        elif(operators == ["mean within years","mean over years"]):
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        elif(operators == ["maximum"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.month])
        elif(operators == ["minimum"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.month])
        elif(operators == ["maximum within days","mean over days"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        elif(operators == ["minimum within days","mean over days"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.day])
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.month])
        else: raise Exception("Unsupported combination of frequency ",freq," with time operators ",operators,"encountered")
        if(mon > 0): cdo.add_operator(cdoapi.cdo_command.select_month_operator,mon)
    elif(freq == "day"):
        if(operators == ["point"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,12)
        elif(operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.day])
        elif(operators == ["mean within years","mean over years"]):
            cdo.add_operator(cdoapi.cdo_command.mean_time_operators[cdoapi.cdo_command.day])
        elif(operators == ["maximum"]):
            cdo.add_operator(cdoapi.cdo_command.max_time_operators[cdoapi.cdo_command.day])
        elif(operators == ["minimum"]):
            cdo.add_operator(cdoapi.cdo_command.min_time_operators[cdoapi.cdo_command.day])
        else: raise Exception("Unsupported combination of frequency ",freq," with time operators ",operators,"encountered")
        if(mon > 0): cdo.add_operator(cdoapi.cdo_command.select_month_operator,mon)
    elif(freq == "6hr"):
        if(operators == ["point"] or operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.select_hour_operator,0,6,12,18)
        else: raise Exception("Unsupported combination of frequency ",freq," with time operators ",operators,"encountered")
    elif(freq in ["1hr","3hr"]):
        if(operators != ["point"] and operators != ["mean"]):
            raise Exception("Unsupported combination of frequency ",freq," with time operators ",operators,"encountered")
    elif(freq == 0):
        if(operators == ["point"] or operators == ["mean"]):
            cdo.add_operator(cdoapi.cdo_command.select_step_operator,1)
        else: raise Exception("Unsupported combination of frequency ",freq," with time operators ",operators,"encountered")
    else: raise Exception("Unsupported frequency ",freq," encountered")


# Translates the cmor vertical level post-processing operation to a cdo command-line option
def add_level_operators(cdo,task):
    global log
    if(task.source.spatial_dims == 2): return
    zdims = getattr(task.target,"z_dims",[])
    if(len(zdims) == 0): return
    if(len(zdims) > 1):
        log.error("Multiple level dimensions in table %s are not supported by this post-processing software",(task.target.table))
    axisname = zdims[0]
    if(axisname == "alevel"):
        cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.modellevel)
    if(axisname == "alevhalf"):
        log.error("Vertical half-levels in table %s are not supported by this post-processing software",(task.target.table))
        return
    axisinfos = cmor_target.get_axis_info(task.target.table)
    axisinfo = axisinfos.get(axisname,None)
    if(not axisinfo):
        log.error("Could not retrieve information for axis %s in table %s" % (axisname,task.target.table))
        return
    oname = axisinfo.get("standard_name",None)
    leveltypes = cdo.get_z_axes(getattr(task,"path",None),task.source.get_root_codes()[0].var_id)
    ml2pl,ml2hl = False,False
    if(oname == "air_pressure"):
        if(cdoapi.cdo_command.pressure_level_code not in leveltypes and cdoapi.cdo_command.hybrid_level_code in leveltypes):
            log.warning("Could not find pressure levels for %s, will interpolate from model levels",task.target.variable)
            cdo.add_operator(cdoapi.cdo_command.select_code_operator,*[134])
            cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.modellevel)
            ml2pl = True
        else:
            cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.pressure)
    elif(oname in ["height","altitude"]):
        if(cdoapi.cdo_command.height_level_code not in leveltypes and cdoapi.cdo_command.hybrid_level_code in leveltypes):
            log.warning("Could not find height levels for %s, will interpolate from model levels",task.target.variable)
            cdo.add_operator(cdoapi.cdo_command.select_code_operator,*[134])
            cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.modellevel)
            ml2hl = True
        else:
            cdo.add_operator(cdoapi.cdo_command.select_z_operator,cdoapi.cdo_command.height)
    elif(axisname not in ["alevel","alevhalf"]):
        log.error("Could not convert vertical axis type %s to CDO axis selection operator" % oname)
        return
    zlevs = axisinfo.get("requested",[])
    if(zlevs == "all"): return
    if(len(zlevs) == 0):
        val = axisinfo.get("value",None)
        if(val): zlevs = [val]
    if(len(zlevs) > 0):
        if(ml2pl):
            cdo.add_operator(cdoapi.cdo_command.ml2pl_operator,*zlevs)
        elif(ml2hl):
            cdo.add_operator(cdoapi.cdo_command.ml2hl_operator,*zlevs)
        else:
            cdo.add_operator(cdoapi.cdo_command.select_lev_operator,*zlevs)
