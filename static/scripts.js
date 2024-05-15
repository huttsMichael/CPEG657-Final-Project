$(document).ready(function() {
    $.getJSON('/column_names', function(data) {
        // Append column headers and footers
        var theadTr = $('#vehicleTable thead tr');
        var tfootTr = $('#vehicleTable tfoot tr');
        data.columns.forEach(function(column, index) {
            theadTr.append('<th>' + column.title + '</th>');
            tfootTr.append('<th><input type="text" placeholder="Search ' + column.title + '" data-index="' + index + '"/></th>');
        });

        // Define default visible columns
        var defaultVisibleColumns = ['make', 'model', 'year'];

        // Initialize DataTable
        var table = $('#vehicleTable').DataTable({
            "ajax": {
                "url": "/fetch_data",
                "data": function(d) {
                    d.columns = data.columns.map(column => column.data);
                    // Add column-specific search values to the request
                    $('#vehicleTable tfoot input').each(function() {
                        var i = $(this).data('index');
                        d[`columns[${i}][search][value]`] = this.value;
                        console.log(`Column ${data.columns[i].data}: Search value = ${this.value}`);
                    });
                    return d;
                }
            },
            "serverSide": true,
            "processing": true,
            "columns": data.columns.map(column => ({
                "data": column.data,
                "title": column.title,
                "defaultContent": "",
                "visible": defaultVisibleColumns.includes(column.data),
                "orderable": true
            })),
            "dom": '<"top"Bf>rt<"bottom"lip><"clear">',
            "buttons": [
                {
                    extend: 'colvis',
                    text: 'Column visibility',
                    className: 'btn-primary',
                    columns: ':not(.noVis)'
                }
            ]
        });

        // Apply the search
        table.columns().every(function() {
            var column = this;
            $('input', column.footer()).on('keyup change clear', function() {
                if (column.search() !== this.value) {
                    column.search(this.value).draw();
                }
            });
        });
    });
});
