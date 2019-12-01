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
            // data='{"0": {"0": "SYS received your job, ID: ", "1": "<strong>4", "2": "</strong>."}, "1": {"0": "Patterns processed/total : <strong>4 / 14</strong>"}, "2": {"0": "Youll get your patterns in "}, "3": {"0": "<strong>nobackup/d_02168_t2/tingchu02168/20180601_non_conformance_single_4</strong>"}}';
            
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
    var groupList = ["group_conformance", "group_non_conformance"];
    for(var i = 0; i < groupList.length; i++) {
        listItems(groupList[i], groupList);
    }

    // Yes button in select list modal
    $("#save").on('click', function() {
        if ($("#showSelected").val() != "") {
            $('#modalConfirm').modal('show');
        } else {
            showCheckedItems();
        }
    });

    // Yes button in confirm modal
    $("#confirm").on('click', function() {
        showCheckedItems();
    });

});

function showCheckedItems() {
    var checkedItems = $("#itemList input:checked");
    var itemStr = "";
    for (var i=0; i<checkedItems.length; i++) {
        itemStr += checkedItems[i].value + "\n";
    }
    $("#showSelected").val(itemStr);
    $("#showSelected").html(itemStr);
}

// Prevent being directed to new page, and change message
$('#form-container').on('submit', function(event) {
    event.preventDefault();
    $.ajax({
        url : $(this).attr('action') || window.location.pathname,
        type: "POST",
        data: $(this).serialize(),
        success: function (data) {
            // parse json to object
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
        },
        error: function (jXHR, textStatus, errorThrown) {
            console.log(errorThrown);
        }
    });
});

//Reset
$("#resetBtn").click(function (e) {
    document.getElementById("form-container").reset();
    $("#showSelected").val("");
});

// "Select all" button on change
$("#selectAll").change(function() {
   if($(this).prop("checked")) {
        $("#groupSelector input").prop("checked", true);
        $("#itemList input").prop("checked", true);
   } else {
        $("#groupSelector input").prop("checked", false);
        $("#itemList input").prop("checked", false);      
   }
});

// Show input format example popup
$("#popupNonCon").on('click mouseover', function () {
    var popup = document.getElementById("inputFormatNonCon");
    popup.classList.toggle("show");
});

// list items
var allItemsMap = [];
function listItems(groupName, groupList) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "data/" + groupName + ".json", true);
    xmlhttp.send();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var myObj = JSON.parse(this.responseText);
            var itemStr = "";
            
            // store item in allItemsMap (Object) with item name and item class
            // class is an array (classArray)
            // each item is unique. If it is already in allItemsMap, the only thing we do is adding a new class.
            for (var k=0; k<myObj.length; k++) {
                var item = myObj[k];
                
                if (item in allItemsMap) {
                    var classArray = allItemsMap[item];
                    classArray.push(groupName);
                    allItemsMap[item] = classArray;
                } else {
                    allItemsMap[item] = [groupName];
                }
            }
            
            // allItemsList is all item names. (Array)
            var allItemsList = Object.keys(allItemsMap);

            for (var k=0; k<allItemsList.length; k++) {
                var itemClass = allItemsMap[allItemsList[k]].toString().replace(",", " ");
                itemStr += "<label><input type='checkbox' class='" + itemClass + "' value='" + allItemsList[k] + "'/>" + allItemsList[k] + "</label>";
            }

            $("#itemList").html(itemStr);

            // add group select all checkbox
            var groupSelectorId = groupName + "SelectAll";
            $("#groupSelector").append("<label><input type='checkbox' id='" + groupSelectorId + "'/><b>" + groupName + "</b></label>");
            
            // Handle check events
            handleItemsCheckEvent(groupName, groupList, groupSelectorId);
        }
    }
}

function handleItemsCheckEvent(groupName, groupList, groupSelectorId) {
    // group select all button on change
    $("#" + groupSelectorId).change(function() {
        if($(this).prop("checked")) {
            $("input." + groupName).prop("checked", true);

            //if all groups are checked, check "Select all"
            var all_groups_selected = true;
            for (var k=0; k<groupList.length; k++) {
                if (!$("#selectAll").prop("checked")) {
                    if (groupList[k] != groupName) {
                        if (!$("#" + groupList[k] + "SelectAll").prop("checked")) {
                            all_groups_selected = false;
                            break;
                        }
                    }
                }
            }
            if (all_groups_selected) {
                $("#selectAll").prop("checked", true);
            }
        } else {
            $("input." + groupName).prop("checked", false); 
            $("#selectAll").prop("checked", false);      
        }
    });

    // uncheck "group select all" if one of the group items is unchecked
    $("." + groupName).change(function() {
        if(!$(this).prop("checked")) {
            $("#" + groupSelectorId).prop("checked", false);
            $("#selectAll").prop("checked", false); 
        }
    });
}