const puppeteer = require('puppeteer');

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    // Load the final HTML file with the user's specific diagram
    await page.goto('file:///C:/patchamomma/prac1/Detailed_Project_Description.html', { waitUntil: 'networkidle0' });
    
    // Generate PDF
    const pdfPath = 'C:/patchamomma/prac1/Detailed_Project_Description.pdf';
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      margin: { top: '30px', right: '30px', bottom: '30px', left: '30px' },
      printBackground: true
    });
    
    await browser.close();
    console.log('Detailed PDF generated at:', pdfPath);
  } catch (err) {
    console.error('Error generating PDF:', err);
  }
})();
