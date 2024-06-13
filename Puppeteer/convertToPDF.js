// convertToPDF.js
const puppeteer = require('puppeteer');

async function convertHTMLToPDF(inputPath, outputPath) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(`file://${inputPath}`, {waitUntil: 'networkidle0'});
    await page.pdf({path: outputPath, format: 'A4'});
    await browser.close();
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];

convertHTMLToPDF(inputPath, outputPath).catch(error => {
    console.error('Fehler bei der Konvertierung:', error);
    process.exit(1);
});
