import logging
from logging.handlers import RotatingFileHandler
from nicegui import ui
from nicegui import app
import httpx

# Configure logger
logger = logging.getLogger("trip_planner")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Inject manifest + service worker + install logic
ui.add_head_html('''
<link rel="manifest" href="/static/manifest.json">
<script>
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    const btn = document.getElementById('installBtn');
    if (btn) btn.style.display = 'inline-block';
});

function installApp() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            } else {
                console.log('User dismissed the install prompt');
            }
            deferredPrompt = null;
            const btn = document.getElementById('installBtn');
            if (btn) btn.style.display = 'none';
        });
    }
}

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/service-worker.js')
        .then(reg => console.log('ServiceWorker registered:', reg))
        .catch(err => console.log('ServiceWorker registration failed:', err));
}
</script>
''')

# UI setup
ui.label('Welcome to the NiceGUI Trip Planner!')
city_input = ui.input('Enter a city name').props('outlined')
result_label = ui.label('')

async def fetch_data():
    city = city_input.value
    if not city:
        result_label.text = 'Please enter a city'
        logger.warning('User submitted empty city input')
        return

    url = f'https://api.api-ninjas.com/v1/city?name={city}'
    headers = {'X-Api-Key': 'YOUR_API_KEY'}  # Replace with your actual key

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            logger.info(f'HTTP Request: GET {url} - Status: {response.status_code}')

            if response.status_code == 200:
                data = response.json()
                if data:
                    result = str(data[0])
                    result_label.text = result
                    logger.info(f'Data fetched for city "{city}": {result}')
                else:
                    result_label.text = 'No data found for this city.'
                    logger.info(f'No data found for city "{city}"')
            else:
                result_label.text = f'Error: {response.status_code}'
                logger.error(f'API returned error for "{city}" - Status: {response.status_code}')
    except Exception as e:
        result_label.text = 'An error occurred while fetching data.'
        logger.exception(f'Exception during API request for city "{city}": {e}')

ui.button('Search', on_click=fetch_data)

# Install App button (hidden initially)
install_btn = ui.button('Install App', on_click=lambda: ui.run_javascript('installApp()'))
install_btn.style('display:none;')
install_btn.id = 'installBtn'

# Serve static files
app.add_static_files('/static', 'static')

# Run the app
ui.run()