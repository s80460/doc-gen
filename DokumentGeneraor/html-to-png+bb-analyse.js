const puppeteer = require('puppeteer');  // Puppeteer wird für die Browser-Automation importiert
const fs = require('fs').promises;       // Das Promise-basierte FileSystem-Modul wird für asynchrone Dateioperationen verwendet
const path = require('path');            // Das Path-Modul wird zur Pfadmanipulation importiert

// Inport und Export-Pfade
const inputDirectoryPath = path.join(__dirname, 'templates/fertigeHTML-Dokumente');
const outputDirectoryPath = path.join(__dirname, 'output');

//JSON-Datei-Ausgabeverzeichnis für die Bounding Boxen
const jsonOutputDirectoryPath = path.join(__dirname, 'bb-erfassen-output');

// Die A4-Abmessungen in Pixel bei einer Auflösung von 300 DPI werden definiert
const A4_WIDTH = 2480;
const A4_HEIGHT = 3508;

// Der SCALE_FACTOR dient dazu, die Seite künstlich zu vergrößern, um eine präzisere Erfassung der Abmessungen und Positionen von Bounding Boxen zu ermöglichen
const SCALE_FACTOR = 2.0; // 200% Skalierung

// Nimmt Seite und einen CSS-Selektor, um relevante Elemente zu identifizieren und deren Bounding Box-Informationen und Text zu extrahieren.
async function captureBoundingBoxesAndText(page, selector) {  
  return await page.evaluate((selector) => { // führt JavaScript-Code in der geöffneten Webseite aus
    const elements = Array.from(document.querySelectorAll(selector)); //findet alle Elemente, die dem übergebenen CSS-Selektor entsprechen
    return elements.map(element => { //Jedes Element des Arrays wird verarbeitet
      const rect = element.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) {
        return null; // Elemente ohne sichtbare Abmessungen werden übersprungen bzw. ignoriert
      }
      let identifier = element.tagName.toLowerCase() === 'img' ? 'image' : element.className || element.id || 'generic_identifier';

      if (identifier === 'generic_identifier') {
        let parent = element.parentElement;
        while (parent && !parent.className && !parent.id) {
          parent = parent.parentElement;
        }
        identifier = parent ? parent.className || parent.id : 'generic_identifier';
      }

      identifier = identifier.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '');

      return {
        identifier: identifier,
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height,
        text: element.tagName.toLowerCase() === 'img' ? '' : element.textContent.trim()
      };
    }).filter(box => box !== null);
  }, selector);
}


// Lädt eine HTML-Datei in Puppeteer, skaliert den Inhalt für eine genauere Erfassung, setzt die Größe des Viewports und extrahiert die Daten der BoundingBoxes.
async function processHtmlFile(browser, filePath, outputDirectoryPath, jsonOutputDirectoryPath) {
  // Der Basisname der Datei wird aus dem Dateipfad extrahiert.
  const fileName = path.basename(filePath);
  // Eine neue Seite im Browser wird geöffnet.
  const page = await browser.newPage();

  // CSS-Selektoren für relevante HTML-Elemente, deren Bounding Boxes und Text erfasst werden sollen. Kann beliebig angepasst werden
  const selector = `
  [class^='hauptueberschrift_'] span, 
  [class^='typueberschrift_'] span, 
  [class^='zwischenueberschrift_'] span, 
  [class^='artikelueberschrift_'] span, 
  [class^='artikel_'] span, 
  img,
  div[class^='td'] > span,
  div[class^='level-'] > span,
  div[class^='level-0_'] > span,
  td[class^='level-0_'] > span,
  div[class^='level-'] > div > span,
  span[class^='level-'] > span,
  [class^='datum_'] span,
  [class^='level-0_'] span,
  [class^='level-0_'] span,
  td > span,
  td[class^='level-0_'] > span,
  .level-0_ > span,
  span,
  strong,
  ol > li > div > span,
  h3 > span
  `;


  try {
    // Navigiert zur HTML-Datei und wartet, bis das DOM vollständig geladen bzw. geparst wurde
    await page.goto(`file://${filePath}`, { waitUntil: 'domcontentloaded' });

    // Skaliert den Inhalt der Seite, um eine genauere Erfassung der Elemente zu ermöglichen
    await page.evaluate((scaleFactor) => {
      document.body.style.zoom = scaleFactor.toString(); 
    }, SCALE_FACTOR);

    // Erfasst die Größe des Dokuments nach der Skalierung
    const documentSize = await page.evaluate(() => ({
      width: document.documentElement.scrollWidth,
      height: document.documentElement.scrollHeight
    }));

    // Setzt die Größe des Viewports auf A4-Format, um die Ausgabe zu standardisieren
    await page.setViewport({ width: A4_WIDTH, height: A4_HEIGHT });

    // Ruft die Funktion auf, die BoundingBoxes + Texte der ausgewählten Elemente erfasst
    const boxes = await captureBoundingBoxesAndText(page, selector);

    // Speichert Screenshot der Seite im PNG-Format
    const outputImagePath = path.join(outputDirectoryPath, fileName.replace(".html", ".png"));
    await page.screenshot({ 
      path: outputImagePath, 
      fullPage: false,
      omitBackground: true,
      clip: { x: 0, y: 0, width: A4_WIDTH, height: A4_HEIGHT } 
    });

    // Speichert die Bounding Box-Daten als JSON-Datei. -> Wird an anderer Stelle im DokumentGenerator auch in YOLO gewandelt
    const outputJsonPath = path.join(jsonOutputDirectoryPath, fileName.replace(".html", "-bboxen.json"));
    await fs.writeFile(outputJsonPath, JSON.stringify(boxes, null, 2));

    console.log(`BoundingBox-Koordinaten inkl. Texte wurden erfolgreich erfasst und gespeichert in ${outputJsonPath}`);

    // Schließt die Seite, um Ressourcen freizugeben
    await page.close();
  } catch (error) {
    // Gibt Fehlermeldungen aus, falls während der Verarbeitung ein Fehler auftritt
    console.error(`Fehler bei Verarbeitung ${fileName}:`, error);
  }
}


// Leeren des Verzeichnisses, um alte Dateien zu entfernen (um es für neue Daten vorzubereiten)
async function emptyDirectory(directoryPath) {
  try {
    const files = await fs.readdir(directoryPath);
    for (const file of files) {
      const filePath = path.join(directoryPath, file);
      await fs.unlink(filePath);
    }
    console.log(`Verzeichnis geleert: ${directoryPath}`);
  } catch (error) {
    if (error.code !== 'ENOENT') {
      console.error(`Fehler beim Leeren des Verzeichniss ${directoryPath}:`, error);
    }
  }
}

// Hauptausführungsroutine (Initialisiert Puppeteer, leert Outputverzeichnisse, verarbeitet HTML-Dateien im Inputverzeichnis, extrahiert Daten + schließt den Browser.)
(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    // deaktiviert Sandbox und Sicherheitsfunktion des Chromium-Browsers (wird nicht gebraucht)
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  await emptyDirectory(outputDirectoryPath);
  await emptyDirectory(jsonOutputDirectoryPath);

  try {
    const files = await fs.readdir(inputDirectoryPath);
    const htmlFiles = files.filter(file => path.extname(file).toLowerCase() === '.html');

    for (const fileName of htmlFiles) {
      const filePath = path.join(inputDirectoryPath, fileName);
      await processHtmlFile(browser, filePath, outputDirectoryPath, jsonOutputDirectoryPath);
      console.log(`Processed ${fileName}`);
    }
  } catch (error) {
    console.error('Fehler beim Lesen des Verzeichnisses oder bei der Verarbeitung von Dateien:', error);
  }

  await browser.close();
  console.log('BoundingBox-Koordinaten wurden erfolgreich erfasst und gespeichert.');
})();
