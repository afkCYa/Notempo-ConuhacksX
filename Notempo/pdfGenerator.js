// PDF Generation Module
// Handles screenshot-to-PDF conversion with intelligent page breaking

/**
 * Find page break boundaries by detecting large blocks of white space (7mm+)
 * @param {ImageData} imageData - Canvas image data
 * @param {number} width - Canvas width
 * @param {number} height - Canvas height
 * @param {number} threshold - White pixel ratio threshold (0-1)
 * @returns {number[]} Array of y-coordinates where to break pages
 */
function findPageBreaks(imageData, width, height, threshold = 0.99) {
    const data = imageData.data;
    let whiteRows = [];
    const MIN_GAP_PX = 26; // 7mm at 96dpi ≈ 26 pixels
    const pageBreaks = [];

    // First, identify which rows are completely white
    for (let y = 0; y < height; y++) {
        let whitePixels = 0;
        let totalPixels = 0;

        for (let x = 0; x < width; x++) {
            const idx = (y * width + x) * 4;
            const r = data[idx];
            const g = data[idx + 1];
            const b = data[idx + 2];
            const a = data[idx + 3];

            totalPixels++;
            // White/light: R, G, B all > 240
            if (r > 240 && g > 240 && b > 240 && a > 200) {
                whitePixels++;
            }
        }

        const whiteRatio = whitePixels / totalPixels;
        if (whiteRatio > threshold) {
            whiteRows.push(y);
        }
    }

    // Now find continuous blocks of white rows
    let blockStart = null;
    for (let i = 0; i < whiteRows.length; i++) {
        if (blockStart === null) {
            blockStart = whiteRows[i];
        } else if (whiteRows[i] !== whiteRows[i - 1] + 1) {
            // Gap detected - end of block
            const blockEnd = whiteRows[i - 1];
            const blockHeight = blockEnd - blockStart;
            
            // Only treat as page break if block is large enough (7mm+)
            if (blockHeight >= MIN_GAP_PX) {
                // Use the middle of the gap as the break point
                pageBreaks.push(Math.floor((blockStart + blockEnd) / 2));
            }
            blockStart = whiteRows[i];
        }
    }

    // Check last block
    if (blockStart !== null) {
        const blockEnd = whiteRows[whiteRows.length - 1];
        const blockHeight = blockEnd - blockStart;
        if (blockHeight >= MIN_GAP_PX) {
            pageBreaks.push(Math.floor((blockStart + blockEnd) / 2));
        }
    }

    return pageBreaks;
}

/**
 * Split canvas into individual pages based on detected break points
 * @param {HTMLCanvasElement} canvas - Source canvas
 * @param {number[]} breaks - Y-coordinates of page breaks
 * @returns {HTMLCanvasElement[]} Array of canvas elements, one per page
 */
function splitCanvasByBreaks(canvas, breaks) {
    const pages = [];
    const A4_HEIGHT_PX = 1122; // A4 at 96dpi (297mm * 96/25.4)
    
    let startY = 0;
    
    for (let i = 0; i <= breaks.length; i++) {
        let endY;
        
        if (i < breaks.length) {
            endY = Math.min(breaks[i], startY + A4_HEIGHT_PX);
        } else {
            endY = canvas.height;
        }

        if (endY - startY > 50) { // Only create page if it has meaningful content
            const ctx = document.createElement('canvas');
            ctx.width = canvas.width;
            ctx.height = endY - startY;
            
            const ctxCtx = ctx.getContext('2d');
            ctxCtx.drawImage(
                canvas,
                0, startY,
                canvas.width, endY - startY,
                0, 0,
                canvas.width, endY - startY
            );
            
            pages.push(ctx);
        }
        
        startY = endY;
        if (startY >= canvas.height) break;
    }

    return pages;
}

/**
 * Generate and download PDF from a container element
 * @param {HTMLElement} container - Container element to capture
 * @param {string} filename - Filename for the downloaded PDF
 */
async function generateAndDownloadPDF(container, filename) {
    try {
        // Capture the full music sheet
        const canvas = await html2canvas(container, {
            scale: 2,
            logging: false,
            allowTaint: true,
            useCORS: true,
            backgroundColor: '#ffffff'
        });

        // Analyze canvas to find page breaks
        const ctx = canvas.getContext('2d');
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pageBreaks = findPageBreaks(imageData, canvas.width, canvas.height);

        // Split canvas into individual pages
        const pages = splitCanvasByBreaks(canvas, pageBreaks);

        // Create PDF
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });

        const pageWidth = pdf.internal.pageSize.getWidth();
        const imgWidth = pageWidth;
        
        // Add each page to PDF
        for (let i = 0; i < pages.length; i++) {
            const pageCanvas = pages[i];
            const imgHeight = (pageCanvas.height / pageCanvas.width) * imgWidth;
            const imgData = pageCanvas.toDataURL('image/png');

            if (i > 0) {
                pdf.addPage();
            }

            pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
        }

        // Download PDF
        const finalFilename = filename ? `${filename}.pdf` : 'sheet.pdf';
        pdf.save(finalFilename);
        return true;
    } catch (err) {
        throw new Error(`PDF generation failed: ${err.message}`);
    }
}
