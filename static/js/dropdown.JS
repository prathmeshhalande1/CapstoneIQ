document.querySelectorAll('.status-option').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault(); 
            const selectedValue = this.getAttribute('data-value');
            document.getElementById('statusInput').value = selectedValue;
            document.getElementById('statusDropdownBtn').innerText = selectedValue;
        });
    });