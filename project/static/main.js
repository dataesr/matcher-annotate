displayStructure = (id, status, match_type) => {
    $.ajax({url: `/${match_type}/${id}`})
        .done(response => {
            html = '<li>';
            for (attribute in response) {
                html += `<div class="${attribute}">`
                html += `${attribute} : `
                if (attribute === 'url') {
                    html += `<a href="${response[attribute]}" target="_blank">${response[attribute]}</a>`
                } else {
                    html += response[attribute]
                }
                html += '</div>'
            }
            html += '</li>'
            $(`.${status} div ul`).html(html);
        });
};

loadData = (log) => {
    $('.type').html(log?.type);
    $('.query').html(log?.query);
    $('.strategy').html(log?.strategy);
    expecteds = log.expected.split(',').filter(expected => expected.length > 0);
    if (expecteds.length === 0) {
        $('.expected div').html('Nothing expected');
    } else {
        for (index in expecteds) {
            displayStructure(id=expecteds[index], status='expected', match_type=log.type);
        }
    }
    matcheds = log.matched.split(',').filter(matched => matched.length > 0);
    if (matcheds.length === 0) {
        $('.matched div').html('Nothing matched');
    } else {
        for (index in matcheds) {
            displayStructure(id=matcheds[index], status='matched', match_type=log.type);
        }
    }
};

// INit
$('.row').hide();

$(document).ready(() => {
    let index = 0;
    $('#previous').prop('disabled', true);
    // Load data
    // TODO: Add spinner while loading data
    $.ajax({url: '/logs'}).done((response) => {
        console.log('DONE');
        logs = [];
        for(i = 0; i < response.logs.length; i++) {
            logs.push(JSON.parse(response.logs[i]));
        }
        loadData(log=logs[index]);
        $('.row').show();
        $('.message').hide();
        $('#next').click(() => {
            // TODO: Add spinner while loading next data
            index++;
            $('#previous').prop('disabled', index === 0);
            $('#next').prop('disabled', index === logs.length - 1);
            loadData(log=logs[index]);
        });
        $('#previous').click(() => {
            // TODO: Add spinner while loading next data
            index--;
            $('#previous').prop('disabled', index === 0);
            $('#next').prop('disabled', index === logs.length - 1);
            loadData(log=logs[index]);
        });
    });
});