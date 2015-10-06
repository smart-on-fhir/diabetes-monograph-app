/*
 * select a sample (callset) from google's 1000 Genomes data set
 */

// callsets by page
var pages = [];
var pageToken;
var addButton = '<li><a href="#" id="add" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>';
var morePageButton = '<li><a href="#" id="more"><span aria-hidden="true">...</span></a></li>';
var label_Sample = '<p id="instruction">Instructions:</p><p id="instructionContent">Please select a sample to continue.</p><p id="label">Samples:</p>';
var loading = '<p id="loading">Loading ... </p>';

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

    // Add the label
    $('#callsets').append(label_Sample);

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
    $('#more').remove();

    $('#add').remove();
    
    $('.active').removeAttr('class');
    $('#callset-pages').append(
            '<li class="active">'+
            '<a class="page" href="#" id="'+pages.length+'">'+
            (pages.length+1)+
            '</a></li>');
    // More Page Button
    $('#callset-pages').append(morePageButton);
    // Add to indicate the total pages
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
        // More Button Action
        $('#more').click(function(){
            ;
        });
       
    });
}

$(document).ready(function() {
    addCallsets();
}) 
