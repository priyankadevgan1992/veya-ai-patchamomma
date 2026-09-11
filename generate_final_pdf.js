const puppeteer = require('puppeteer');

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    // Load the final HTML file with the user's specific diagram
    await page.goto('file:///C:/patchamomma/prac1/Veya_Tech_Documentation_Final.html', { waitUntil: 'networkidle0' });
    
    // Generate PDF
    const pdfPath = 'C:/patchamomma/prac1/Veya_Tech_Documentation_Final.pdf';
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      margin: { top: '20px', right: '20px', bottom: '20px', left: '20px' },
      printBackground: true
    });
    
    await browser.close();
    console.log('Final PDF generated at:', pdfPath);
  } catch (err) {
    console.error('Error generating PDF:', err);
  }
})();
