require('dotenv').config();  // Load environment variables

const express = require('express');
const mysql = require('mysql2');
const nodemailer = require('nodemailer');
const twilio = require('twilio');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const port = 3000;

// Middleware
app.use(bodyParser.json());
app.use(cors());

// Database connection
const db = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
});

db.connect(err => {
    if (err) {
        console.error('Error connecting to the database:', err);
        return;
    }
    console.log('Connected to the database.');
});

// Twilio configuration
const twilioClient = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

// Endpoint to book an appointment
app.post('/book', async (req, res) => {
    const { date, time, email, phone } = req.body;

    const checkQuery = `SELECT * FROM appointments WHERE date = ? AND time = ? AND reserved = 1`;
    db.query(checkQuery, [date, time], (err, results) => {
        if (err) return res.status(500).send('Database error');
        if (results.length > 0) return res.status(400).send('This slot is already reserved.');

        const insertQuery = `INSERT INTO appointments (date, time, reserved) VALUES (?, ?, 1)`;
        db.query(insertQuery, [date, time], async (err, result) => {
            if (err) return res.status(500).send('Database error');

            // Send email
            try {
                const transporter = nodemailer.createTransport({
                    service: 'gmail',
                    auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASS }
                });
                const mailOptions = {
                    from: process.env.EMAIL_USER,
                    to: email,
                    subject: 'Tithing Appointment Confirmation',
                    text: `Your appointment on ${date} at ${time} has been confirmed.`
                };
                await transporter.sendMail(mailOptions);
            } catch (err) {
                console.error('Email error:', err);
            }

            // Send SMS
            try {
                await twilioClient.messages.create({
                    body: `Your tithing appointment on ${date} at ${time} is confirmed.`,
                    from: process.env.TWILIO_PHONE_NUMBER, // Replace with your Twilio number
                    to: phone
                });
            } catch (err) {
                console.error('SMS error:', err);
            }

            res.send('Appointment booked successfully!');
        });
    });
});

app.listen(port, () => console.log(`Server running on http://localhost:${port}`));
