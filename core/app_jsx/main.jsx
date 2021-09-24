/*
MIT License

Copyright (c) 2021 richardHaw

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

// @include "init.jsxinc"


try {
    undefined.dummyError()
}
catch(e){
    // reserved
}


(function(){
    function NagareObj(){
        /*
        the NagareObj object
        */

        this.graph_path = null;
        this.datablock = null;
        this.bat_path = null;
        this.score_json = null;
        this.strict = true;
        this.propagate = false;
    }
    $.global.NagareObj = NagareObj;


    NagareObj.prototype.init = function(graph_path,datablock,bat_path){
        /*
        safe init
        */

        this.setGraphPath(graph_path);
        this.setDatablock(datablock);
        this.setBatPath(bat_path);
    }


    NagareObj.prototype.setGraphPath = function(graph_path){
        /*
        graph_path setter
        */

        if (graph_path.indexOf(".json") == -1){
            throw new Error("Not a json file: " + graph_path);
        }

        if (! new File(graph_path).exists){
            throw new Error("Not found: " + graph_path);
        }

        this.graph_path = graph_path;
    }


    NagareObj.prototype.setDatablock = function(datablock){
        /*
        datablock setter
        */

        if (! datablock instanceof Object){
            throw new Error("Failed to set datablock (not an object)...");
        }

        this.datablock = datablock;
    }


    NagareObj.prototype.setBatPath = function(bat_path){
        /*
        bat_path setter
        */

        if (bat_path.indexOf(".bat") == -1){
            throw new Error("Not a bat file: " + bat_path);
        }

        const _tmp = new File(bat_path);
        if (! _tmp.parent.exists){
            _tmp.parent.create();
        }

        this.bat_path = _tmp.fsName;
        this.score_json = this.bat_path.replace(".bat",".json");
    }


    NagareObj.prototype.setDebug = function(val){
        /*
        global debug setter
        */

        if (! val instanceof Boolean){
            return;
        }

        $.global.DEBUG = val;
    }


    NagareObj.prototype.setStrict = function(val){
        /*
        strict mode setter
        */

        if (! val instanceof Boolean){
            return;
        }

        this.strict = val;
    }


    NagareObj.prototype.setPropagate = function(val){
        /*
        propagate mode setter
        */

        if (! val instanceof Boolean){
            return;
        }

        this.propagate = val;
    }


    NagareObj.prototype.run = function(){
        /*
        run graph
        */

        InitLogger();
        LOG("Running graph: " + this.graph_path);
        this.scores = this.processTree();
        const score_file = io_utils.writeFile(this.score_json,this.scores);
        LOG("");
        LOG(gen_utils.longSep());
        LOG("Final score: " + score_file.fsName);
    }


    NagareObj.prototype.show = function(){
        /*
        create and run bat to display score
        */

        this.new_bat = this.createBats();
        if (! this.new_bat.execute()){
            alert("Failed to run: " + this.new_bat.fsName);
        }
        LOG("Batch file: " + this.new_bat.fsName);
    }


    NagareObj.prototype.createBats = function(){
        if (NAGARE_ROOT === null){
            throw new Error('Environment variable "NAGARE_ROOT" not set...');
        }

        const pybat_path = this.bat_path.replace(".bat",".py");
        const vbsbat_path = this.bat_path.replace(".bat",".vbs");
        const score_path = this.bat_path.replace(".bat",".json");
        const nagare_root = io_utils.safePath(NAGARE_ROOT);

        // bat
        const bat_nfo = new Array();
        bat_nfo.push("@echo off");

        // bat_nfo.push("python " + nagare_root + "/batman.py %*");
        bat_nfo.push('python "' + pybat_path + '" %*');
        bat_nfo.push("IF %ERRORLEVEL% NEQ 0 (pause)");
        const run_bat = io_utils.writeFile(this.bat_path,bat_nfo.join("\n"));
        const bat_file = new File(this.bat_path);

        // py
        const py_nfo = new Array();
        py_nfo.push("import sys");
        py_nfo.push('sys.path.append(r\"' + new Folder(nagare_root).parent.fsName + '\")');

        if (DEBUG){
            py_nfo.push('for i in sys.path: print(i)');
        }

        py_nfo.push("import nagare");
        py_nfo.push('nagare.Viewer(r\"' + this.graph_path + '"\, r\"' + score_path + '\")');
        const py_bat = io_utils.writeFile(pybat_path,py_nfo.join("\n"));

        // vbs
        const vbs_nfo = new Array();
        vbs_nfo.push('Set WshShell = CreateObject("WScript.Shell")');
        vbs_nfo.push('WshShell.Run chr(34) & "' + bat_file.fsName + '" & Chr(34), 0');
        vbs_nfo.push('Set WshShell = Nothing');
        const vbs_bat = io_utils.writeFile(vbsbat_path,vbs_nfo.join("\n"));
        const vbs_file = new File(vbsbat_path);

        // done
        if (DEBUG){
            return bat_file;
        }
        return vbs_file;
    }


    NagareObj.prototype.processTree = function(){
        const tmp_tree = new TreeDummy();

        // setup
        tmp_tree.STRICT = this.strict;
        tmp_tree.PROPAGATE = this.propagate;
        tmp_tree.DATABLOCK = this.datablock;

        // run
        const tester_obj = io_utils.parseJson(this.graph_path);
        LOG("Strict: " + tmp_tree.STRICT);
        LOG("Propagate: " + tmp_tree.PROPAGATE);
        Recurser(tmp_tree,tester_obj.nodes,tmp_tree.DATABLOCK);

        // done
        return tmp_tree.extractScore(true);
    }


    function Recurser(Spawn_obj,node_data,datablock){
        /*
        main logic
        */

        // early recursion stop
        const failed_count = Spawn_obj.failedNodes().length;

        if (Spawn_obj.STRICT && failed_count){
            return;
        }

        // $.sleep(50);
        LOG("");
        LOG(gen_utils.longSep());

        var _dummy = new NodeDummy(node_data);

        // inject a new key for feedback
        LOG("Running: " + _dummy.name);
        _dummy.dirty = true;
        _dummy.addMessage(_dummy.name+"'s report:");

        // copy the data block
        var _copy_block = new Object();

        if (Spawn_obj.PROPAGATE){
            _copy_block = datablock;
        }
        else {
            _copy_block = JSON.parse(JSON.stringify(datablock));
        }

        // if there's no commands (starter)
        if (_dummy.command == undefined){
            const _dummy_len= _dummy.out_nodes.length;

            for (var d = 0; d < _dummy_len; d++){
                Recurser(Spawn_obj,_dummy.out_nodes[d],_copy_block);
            }

            // this function actually ends here
            return;
        }

        // recurse with commands
        const mod_split = _dummy.command.split(".");
        const mod_name = mod_split[mod_split.length - 1];
        const module_str = mod_split.join("/");
        const mod_path = (Spawn_obj.MOD_ROOT + "/" + module_str + ".jsxinc");

        // find module
        const mod_file = new File(mod_path);
        if (mod_file.exists){
            LOG(mod_name+" --> MODULE: " + mod_path);
        }
        else {
            LOG(mod_name+" --> NOT FOUND: " + mod_path);
        }

        // import the module
        var _exception_msg = "No Exception message..."
        var _run_result = undefined;

        try {
            eval("$.global." + mod_name + " = undefined;");
            eval('// @include \"' + mod_path + '\";');
            eval("_run_result = " + mod_name + ".main(_copy_block);");
            eval("delete " + mod_name + ";");
        }
        catch(err){
            _exception_msg = err.message;
        }

        // used for safety
        if (_run_result instanceof Object === false){
            _run_result = new ResultObj();
            _run_result.setStatus("error");
            _run_result.addMessage("Failed module: " + module_str);
            _run_result.addMessage("@ Error (exception): " + _dummy.name);
            _run_result.addMessage(_exception_msg);
        }

        // after running
        if (! gen_utils.objectInList(_dummy,Spawn_obj.NODES_ALL)){
            Spawn_obj.NODES_ALL.push(_dummy);
        }

        // used for failed or skip
        if (_run_result instanceof ResultObj){
            _dummy.appendMessages(_run_result.getMessages());
            _dummy.setErrors(_run_result.getErrors());

            if (_run_result.getStatus() === "error"){
                _dummy.error = true;
                _dummy.addMessage("@ Error running: " + _dummy.name);
                LOG(JSON.stringify(_copy_block));

                // strict
                if (Spawn_obj.STRICT === true){
                    LOG("Critical: Operation stopped.");
                    return;
                }
            }
            else if (_run_result.getStatus() === "skip"){
                _dummy.skip = true;
                var skip_m = "Skip down-stream evaluation: " + _dummy.name;
                _dummy.addMessage(skip_m);
                LOG(skip_m);
            }

            return _dummy;
        }

        // run out nodes
        for (var _d = 0; _d < _dummy.out_nodes.length; _d++){
            var out_conn = Recurser(Spawn_obj,_dummy.out_nodes[_d],_copy_block);
        }

        // done
        _dummy.addMessage("Success");
        return _dummy;
    }


    function CreateNagare(json_path,datablock,bat_path,strict,propagate,debug){
        /*
        use this to return an instance of NagareObj
        */

        var strict = (strict !== undefined) ? strict : false;
        var propagate = (propagate !== undefined) ? propagate : false;
        var debug = (debug !== undefined) ? debug : false;

        const out = new NagareObj();
        out.init(json_path,datablock,bat_path);
        out.setStrict(strict);
        out.setPropagate(propagate);
        out.setDebug(debug);

        return out;
    }
    $.global.CreateNagare = CreateNagare;

})();



/*
// @include "C:/repo/nagare/core/app_jsx/main.jsx";

var test_block = {
    what: "This is Haw-dini (on Javascript!!!)",
    where: "Made in Japan",
    when: "On my spare time.", // why = "To make a better world",
    who: "Richard Haw"
    }

var session = CreateNagare("C:/repo/nagare/graphs/tester_jsx.json",test_block,"C:/repo/nagare/batman.bat");
session.setDebug(true);
session.run();
session.show();
*/