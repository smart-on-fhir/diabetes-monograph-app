/*
 * select a sample (callset) from google's 1000 Genomes data set
 */

// callsets by page
var pages = [];
var pageToken;
var addButton = '<li><a href="#" id="add" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>';
var loading = '<p id="loading">Loading ... </P>';

// create html for a callset
function renderCallset(callset) {
    console.log(callset);
    return '<a id="'+callset.id+'" class="list-group-item callset">'+
        callset.sampleId+
        '</a>'; 
}

function showCallsets(index) {
    $('.active').removeAttr('class');
    $('#'+index).attr('class', 'active');
    $('#callsets').empty();
    var callsets = pages[index];
    for (var i = 0; i < callsets.length; i++) {
        var callset = callsets[i];
        $('#callsets').append(renderCallset(callset));
    }
    // click to select a sample
    $('.callset').click(function() { 
        var callsetId = $(this).attr('id'); 
        window.location.replace('/select-sample?sample_id='+callsetId); 
    });
}

function addCallsets() { 
    var paging = pageToken ? 'pageToken='+pageToken : '';
    $('#add').remove();
    $('.active').removeAttr('class');
    $('#callset-pages').append(
            '<li class="active">'+
            '<a class="page" href="#" id="'+pages.length+'">'+
            (pages.length+1)+
            '</a></li>');
    $('#callset-pages').append(addButton);
    $('#callsets').empty();
    $('#callsets').append(loading);
    $.getJSON('/callsets?'+paging, function(resp) { 
        pageToken = resp.nextPageToken;
        pages.push(resp.callSets); 
        $('.page').click(function() {
            showCallsets($(this).attr('id'));
        });
        showCallsets(pages.length - 1);
        $('#add').click(function() {
            addCallsets();
        });
    });
}

$(document).ready(function() {
    addCallsets();
}) 
