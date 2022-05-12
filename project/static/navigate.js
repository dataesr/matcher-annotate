displayStructure = (id, status, matcher_type) => {
    if (matcher_type) {
        $.ajax({url: `/${matcher_type}/${id}`})
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
            $(`.${status} div ul`).append(html);
        });
    } else {
        console.error('The matcher type is missing, please check your logs file.');
    }
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
            displayStructure(id=expecteds[index], 'expected', matcher_type=log.type);
        }
    }
    matcheds = log.matched.split(',').filter(matched => matched.length > 0);
    if (matcheds.length === 0) {
        $('.matched div').html('Nothing matched');
    } else {
        for (index in matcheds) {
            displayStructure(id=matcheds[index], 'matched', matcher_type=log.type);
        }
    }
};

// Init
$('.row').hide();

$(document).ready(() => {
    let index = 0;
    $('.actions .previous').prop('disabled', true);
    // Load data
    $.ajax({url: '/logs'}).done((response) => {
        logs = [];
        for(i = 0; i < response.logs.length; i++) {
            logs.push(JSON.parse(response.logs[i]));
        }
        loadData(log=logs[index]);
        $('.row').show();
        $('.message').hide();
        $('.actions .next').click(() => {
            index++;
            $('.actions .previous').prop('disabled', index === 0);
            $('.actions .next').prop('disabled', index === logs.length - 1);
            $('.expected div').html('<ul></ul>');
            $('.matched div').html('<ul></ul>');
            loadData(log=logs[index]);
        });
        $('.actions .previous').click(() => {
            index--;
            $('.actions .previous').prop('disabled', index === 0);
            $('.actions .next').prop('disabled', index === logs.length - 1);
            $('.expected div').html('<ul></ul>');
            $('.matched div').html('<ul></ul>');
            loadData(log=logs[index]);
        });
    });
});