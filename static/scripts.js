$(document).ready(function() {
    $.getJSON('/column_names', function(data) {
        // Append column headers and footers
        var theadTr = $('#vehicleTable thead tr');
        var tfootTr = $('#vehicleTable tfoot tr');
        data.columns.forEach(function(column) {
            theadTr.append('<th>' + column.title + '</th>');
            tfootTr.append('<th>' +
                '<input type="text" placeholder="Search ' + column.title + '" />' +
                '<br>' +
                '<input type="number" placeholder="Min" style="width: 45%;" />' +
                '<input type="number" placeholder="Max" style="width: 45%;" />' +
                '</th>');
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
                    d.columns.forEach((col, i) => {
                        var searchValue = $(`#vehicleTable tfoot tr th:eq(${i}) input[type="text"]`).val();
                        d[`columns[${i}][search][value]`] = searchValue;
                        var minValue = $(`#vehicleTable tfoot tr th:eq(${i}) input[placeholder="Min"]`).val();
                        var maxValue = $(`#vehicleTable tfoot tr th:eq(${i}) input[placeholder="Max"]`).val();
                        d[`columns[${i}][search][min]`] = minValue;
                        d[`columns[${i}][search][max]`] = maxValue;
                        console.log(`Column ${col}: Search value = ${searchValue}, Min = ${minValue}, Max = ${maxValue}`);
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
            $('input[type="text"]', column.footer()).on('keyup change clear', function() {
                if (column.search() !== this.value) {
                    column.search(this.value).draw();
                }
            });

            $('input[type="number"]', column.footer()).on('keyup change clear', function() {
                table.draw();
            });
        });
    });
});
