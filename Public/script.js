document.getElementById('appointment-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = {
        date: formData.get('date'),
        time: formData.get('time'),
        email: formData.get('email'),
        phone: formData.get('phone')
    };

    fetch('http://localhost:3000/book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('response-message').textContent = 'Appointment booked successfully!';
    })
    .catch(error => {
        document.getElementById('response-message').textContent = 'Error: ' + error.message;
    });
});
