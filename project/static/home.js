$(document).ready(() => {
    $('.actions .check').click(() => {
        $.ajax({url: '/check'}).done((response) => {
            html = '<table>';
            html += '<tr><th>Strategy</th><th>Count</th><th>Precision</th><th>True Positiv</th></tr>'
            strategies = Object.keys(response);
            for(i = 0; i < strategies.length; i++) {
                const strategy = strategies[i];
                const { count, precision, vp } = response[strategy];
                html += `<tr><td>${strategy}</td><td>${count}</td><td>${precision}</td><td>${vp}</td></tr>`;
            };
            html += '</table>'
            $('.results').html(html);
        });
    });
});