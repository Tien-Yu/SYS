$( document ).ready(function() {
    $(".ui-wrapper").css('padding-bottom','').css('padding-right','').css('height','').css('width','');
    $("#showSelectedNon").css('height','').css('width','100%');
    // get message on document ready
    $.ajax({
        url : "/js/message" || window.location.pathname,
        type: "GET",
        data: $(this).serialize(),
        success: function (data) {
            // For testing without server messages
            //data='{"0": {"0": "SYS received your job, ID: ", "1": "<strong>4", "2": "</strong>."}, "1": {"0": "Patterns processed/total : <strong>4 / 14</strong>"}, "2": {"0": "Youll get your patterns in "}, "3": {"0": "<strong>nobackup/d_02168_t2/tingchu02168/20180601_non_conformance_single_4</strong>"}}';
            
            // parse json to object
            var myObj = JSON.parse(data);

            //parse object to array
            var text = Object.keys(myObj).map(function (key) { return myObj[key]; });
            var str = "";
            for(var i = 0; i < text.length; i++) {
                if(Object.keys(text[i]).length !== 0) {
                    text[i] = Object.keys(text[i]).map(function (key) { return text[i][key]; });
                    str += "<li>"+text[i].join("") + "</li>";
                }
            }

            // insert into message box
            $("#message").html(str);
        },
        error: function (jXHR, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    });

    // List options in dialog
    listOptions("data/group_non_conformance.json", "non_options", "nonConformance", "selectAllNonId");
    listOptions("data/group_conformance.json", "options", "conformance", "selectAllId");
});

// Prevent being directed to new page, and change message
$('#container').on('submit', function(event) {
    event.preventDefault();
    $.ajax({
        url : $(this).attr('action') || window.location.pathname,
        type: "POST",
        data: $(this).serialize(),
        success: function (data) {
            // parse json to object
            console.log(typeof(data));
            var myObj = JSON.parse(data);

            //parse object to array
            var text = Object.keys(myObj).map(function (key) { return myObj[key]; });
            var str = "";
            for(var i = 0; i < text.length; i++) {
                if(Object.keys(text[i]).length !== 0) {
                    text[i] = Object.keys(text[i]).map(function (key) { return text[i][key]; });
                    str += "<li>"+text[i].join("")+"</li>";
                }
            }

            // insert into message box
            $("#message").html(str);

            // animation
            $("#message-container").css({"animation": "pulse 3s infinite"});
            setTimeout(function(){ $("#message-container").css({"animation": "none", "box-shadow": "none"}); }, 3000);
            $("#submitBtn").css({"animation": "pulseBtn 1.5s infinite"});
            setTimeout(function(){ $("#submitBtn").css({"animation": "none", "box-shadow": "none"}); }, 1500);
        },
        error: function (jXHR, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    });
});

//Reset
$("#resetBtn").click(function (e) {
    document.getElementById("container").reset();
    $("#showSelectedNon").val("");
    $("#showSelected").val("");
    // feedback animation
    $(this).css({"animation": "pulseBtn 1.5s infinite"});
    setTimeout(function(){ $("#resetBtn").css({"animation": "none", "box-shadow": "none"}); }, 1500);
});

// "Select all" buttons in two dialogs
$("#selectAllNonId").change(function() {
   if($("#selectAllNonId").prop("checked")) {
        $("input[name='nonConformance']").prop("checked", true); // select all
   } else {
        $("input[name='nonConformance']").prop("checked", false); // unselect all       
   }
});
$("#selectAllId").change(function() {
   if($("#selectAllId").prop("checked")) {
        $("input[name='conformance']").prop("checked", true);
   } else {
        $("input[name='conformance']").prop("checked", false);          
   }
});

// Show input format example popup
$("#popupNonCon").on('click mouseover', function () {
    var popup = document.getElementById("inputFormatNonCon");
    popup.classList.toggle("show");
});
$("#popupCon").on('click mouseover', function () {
    var popup = document.getElementById("inputFormatCon");
    popup.classList.toggle("show");
});

// Check if user input something in textarea manually
var inputManuallyNon = false;
var inputManually = false;
$("#showSelectedNon").on('input', function () {
    inputManuallyNon = true
});
$("#showSelected").on('input', function () {
    inputManually = true
});

//
$("#showSelectedNon").resizable({
    handles: 's',
    resize: function() {
        $("#nonConformanceSection").height($("#showSelectedNon").height()+150);
    }
});
$("#showSelected").resizable({
    handles: 's',
    resize: function() {
        $("#conformanceSection").height($("#showSelected").height()+150);
    }
});

// Open dialog
$("#nonConformanceBtn").click(function (e) {
    initializeDialog("#nonConformanceDialog", "nonConformance", "#showSelectedNon", inputManuallyNon);  
});
$("#conformanceBtn").click(function (e) {
    initializeDialog("#conformanceDialog","conformance", "#showSelected", inputManually);
});

function initializeDialog(dialogId, checkboxName, showAreaId, manualInput) {
    $( dialogId ).dialog({
        width: "auto",
        height: 700,
        fluid: true, //new option
        buttons: {
            "Ok": function() {
                var replace = true;
                if (manualInput) {
                    var answer = confirm("Do you want to replace the original ones?")
                    if (!answer) {
                        replace = false;
                    }
                }
                if(replace) {                    
                    // show selected items in textarea
                    var str="";
                    var checked = document.querySelectorAll("input[name='"+checkboxName+"']:checked");
                    for (var i = 0; i < checked.length; i++) {
                        str += (i == checked.length-1) ? checked[i].value : (checked[i].value + "\n");
                    }
                    $(showAreaId).val(str);
                    // close dialog
                    $(this).dialog("close");
                }
            },
            "Cancel": function() {
                $(this).dialog("close");
            }
        },
        position: {
            at: "center center"
        }
    });
}

function listOptions(file, id, name, selectAll) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", file, true);
    xmlhttp.send();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var myObj = JSON.parse(this.responseText);
            // Insert elements to tables. Elements order: [1 4; 2 5; 3 6;]
            for (var k=0; k<myObj.length; k++){
                if(k < myObj.length/2) {
                    var table = document.getElementById(id+"1");
                    var row = table.insertRow(k);
                    var cell = row.insertCell(0);
                }
                else {
                    var table = document.getElementById(id+"2");
                    var row = table.insertRow(k-Math.floor(myObj.length/2)-1);
                    var cell = row.insertCell(0);
                }
                cell.innerHTML = "<label><input type='checkbox' class='" + name + "' name='" + name + "' value='" + myObj[k] + "'/>" + myObj[k] + "</label>"; 
            }

            // When "Select all" is checked, if any of options is changed to unckecked, unchecked "Select all".
            $("input:checkbox[name='" + name + "']").change(function() {
                if ($("#"+selectAll).prop("checked") == true) {
                    $("input:checkbox[name='" + name + "']").each(function() {  
                        if($(this).prop("checked") == false) {  
                            $("#"+selectAll).removeAttr("checked");
                            return false;
                        }
                    }); 
                }
            });
        }
    }; 
}