const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());
app.use(cors());

app.post('/optimize', (req, res) => {
    const { start, end, vehicleType } = req.body;

    // Mock route data
    const route = {
        type: 'FeatureCollection',
        features: [
            {
                type: 'Feature',
                geometry: {
                    type: 'LineString',
                    coordinates: [
                        [start.split(',')[1], start.split(',')[0]],
                        [end.split(',')[1], end.split(',')[0]],
                    ],
                },
            },
        ],
    };

    // Mock route details
    const distance = 15000; // in meters
    const duration = 1200; // in seconds
    const emissions = 100.5; // in grams

    res.json({ route, distance, duration, emissions });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
