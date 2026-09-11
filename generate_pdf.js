const puppeteer = require('puppeteer');

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    // Load the local HTML file
    await page.goto('file:///C:/patchamomma/prac1/veya_tech_documentation.html', { waitUntil: 'networkidle0' });
    
    // Wait a brief moment to ensure Mermaid finishes rendering the SVG
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Generate PDF
    const pdfPath = 'C:/patchamomma/prac1/Veya_Tech_Documentation.pdf';
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      margin: { top: '20px', right: '20px', bottom: '20px', left: '20px' },
      printBackground: true
    });
    
    await browser.close();
    console.log('PDF generated at:', pdfPath);
  } catch (err) {
    console.error('Error generating PDF:', err);
  }
})();
