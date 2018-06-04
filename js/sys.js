$( document ).ready(function() {
    // get message on document ready
    $.ajax({
        url : "/js/message" || window.location.pathname,
        type: "GET",
        data: $(this).serialize(),
        success: function (data) {
            //data='{"first": "Currently you have 1 job (ID: ","idVal": "4","second": ") still running.","third": "You will get your patterns in ","path": "nobackup/d_02168_t2/tingchu02168/20180601_non_conformance_single_4"}'
            var myObj = JSON.parse(data);
            var first = myObj.first;
            var id = "<b>" + myObj.idVal + "</b>";
            var second = myObj.second + "</br></br>";
            var third = myObj.third;
            var path = "</br><b>" + myObj.path + "</b>";
            $("#message").html(first + id + second + third + path);

        },
        error: function (jXHR, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
    // List options in dialog
    listOptions("data/group_non_conformance.json", "non_options", "nonConformance", "selectAllNonId");
    listOptions("data/group_conformance.json", "options", "conformance", "selectAllId");
});

// Prevent being directed to new page
$('#container').on('submit', function(event) {
    event.preventDefault();
    $.ajax({
        url : $(this).attr('action') || window.location.pathname,
        type: "POST",
        data: $(this).serialize(),
        success: function (data) {
            data='{"first": "Currently you have 1 job (ID: ","idVal": "4","second": ") still running.","third": "You will get your patterns in ","path": "nobackup/d_02168_t2/tingchu02168/20180601_non_conformance_single_4"}'
            var myObj = JSON.parse(data);
            var first = myObj.first;
            var id = "<b>" + myObj.idVal + "</b>";
            var second = myObj.second + "</br></br>";
            var third = myObj.third;
            var path = "</br><b>" + myObj.path + "</b>";
            $("#message").html(first + id + second + third + path);
        },
        error: function (jXHR, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
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

// Open dialog
$("#nonConformanceBtn").click(function (e) {
    initializeDialog("#nonConformanceDialog", "nonConformance", "#showSelectedNon");  
});
$("#conformanceBtn").click(function (e) {
    initializeDialog("#conformanceDialog","conformance", "#showSelected");
});

function initializeDialog(dialogId, checkboxName, showAreaId) {
    $( dialogId ).dialog({
        width: "auto",
        height: 700,
        fluid: true, //new option
        buttons: {
            "Ok": function() {
                // show selected items in textarea
                var str="";
                var checked = document.querySelectorAll("input[name='"+checkboxName+"']:checked");
                for (var i = 0; i < checked.length; i++) {
                    str += (i == checked.length-1) ? checked[i].value : (checked[i].value + ", ");
                }
                $(showAreaId).val(str);

                // close dialog
                $(this).dialog("close");
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