const puppeteer = require('puppeteer');

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    // Point to the standalone HTML file we just created
    await page.goto('file:///C:/patchamomma/prac1/Testing_Instructions_Standalone.html', { waitUntil: 'networkidle0' });
    
    // Generate the PDF
    const pdfPath = 'C:/patchamomma/prac1/Testing_Instructions_Standalone.pdf';
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      margin: { top: '30px', right: '30px', bottom: '30px', left: '30px' },
      printBackground: true
    });
    
    await browser.close();
    console.log('Testing PDF generated at:', pdfPath);
  } catch (err) {
    console.error('Error generating PDF:', err);
  }
})();
