// puppeteer in JS, statt wkhtmltoimage in Python


const puppeteer = require('puppeteer');

async function convertHTMLToA4Image(inputPath, outputPath) {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 1 });
        await page.goto(`file://${inputPath}`, { waitUntil: 'networkidle2' });
        await page.screenshot({ path: outputPath, fullPage: true });
        await browser.close();
    } catch (error) {
        console.error('Fehler beim Konvertieren der HTML zu PNG:', error);
        process.exit(1); // Beendet den Prozess mit einem Fehlerstatus
    }
}

const args = process.argv.slice(2); // Nimmt Argumente vom Benutzer entgegen
convertHTMLToA4Image(args[0], args[1]);
