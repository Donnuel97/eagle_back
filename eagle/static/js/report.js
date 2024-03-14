document.getElementById('downloadexcel').addEventListener('click', function() {
    var table2excel = new Table2Excel();
    table2excel.export(document.getElementById("table"));
  });

  window.onload = function () {
    document.getElementById("export-pdf")
        .addEventListener("click", () => {
            const invoice = this.document.getElementById("table");
            console.log(table);
            console.log(window);
            var opt = {
                margin: 1,
                filename: 'Report.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().from(table).set(opt).save();
        })
}