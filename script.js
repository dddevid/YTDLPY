// Main script for YTDLPY web interface
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const urlInput = document.getElementById('url-input');
    const pasteBtn = document.getElementById('paste-btn');
    const selectFolderBtn = document.getElementById('select-folder-btn');
    const outputPathEl = document.getElementById('output-path');
    const downloadBtn = document.getElementById('download-btn');
    const resultStatus = document.getElementById('result-status');
    const progressModal = document.getElementById('progress-modal');
    const modalStatus = document.getElementById('modal-status');
    const progressBar = document.getElementById('progress');
    const progressText = document.getElementById('progress-text');
    const progressFile = document.getElementById('progress-file');
    const progressStats = document.getElementById('progress-stats');
    const logText = document.getElementById('log-text');
    const instructionsBtn = document.getElementById('instructions-btn');
    const githubLink = document.getElementById('github-link');
    
    // Variabile per memorizzare il percorso del file scaricato
    let downloadedFilePath = '';
    
    // Variabili per il calcolo dell'ETA
    let downloadStartTime = null;
    let downloadPreviousBytes = 0;
    let downloadPreviousTime = null;
    let downloadSpeedHistory = [];
    const MAX_SPEED_HISTORY = 5; // Mantieni una storia delle ultime 5 velocità per una media più stabile

    // Current output directory
    let currentOutputDir = null;
    
    // Inizializza l'applicazione
    window.appInitialized = true;
    
    // Se ci sono update in sospeso, processiamoli ora
    if (window.pendingProgressUpdates && window.pendingProgressUpdates.length > 0) {
        console.log('Processing pending updates:', window.pendingProgressUpdates.length);
        window.pendingProgressUpdates.forEach(data => {
            window.updateProgressUI(data);
        });
        window.pendingProgressUpdates = [];
    }
    
    // Create pywebview bridge to communicate with Python
    function initializePyWebViewBridge() {
        window.addEventListener('pywebviewready', function() {
            // Set default output dir
            window.pywebview.api.get_default_output_dir().then(dir => {
                currentOutputDir = dir;
                outputPathEl.textContent = formatPath(dir);
            });
        });
    }
    
    // Format long paths for display
    function formatPath(path) {
        if (path.length > 30) {
            return '...' + path.slice(-27);
        }
        return path;
    }

    // Button event listeners
    pasteBtn.addEventListener('click', function() {
        // Use pywebview clipboard API
        if (window.pywebview) {
            window.pywebview.api.get_clipboard_text().then(text => {
                if (text) {
                    // Assicuriamoci che text sia una stringa
                    const clipText = typeof text === 'string' ? text : String(text);
                    
                    // Rimuovi eventuali caratteri di controllo che potrebbero causare problemi
                    const cleanText = clipText.replace(/[\u0000-\u001F\u007F-\u009F]/g, '');
                    
                    // Aggiorna il campo input
                    urlInput.value = cleanText;
                    
                    // Log per debug
                    console.log("Testo incollato:", cleanText);
                }
            }).catch(err => {
                console.error('Errore nell\'accesso alla clipboard:', err);
                // Fallback usando il browser API
                fallbackClipboardRead();
            });
        } else {
            // Fallback per test nel browser
            fallbackClipboardRead();
        }
    });

    // Funzione di fallback per la lettura della clipboard nel browser
    function fallbackClipboardRead() {
        navigator.clipboard.readText().then(text => {
            urlInput.value = text;
        }).catch(err => {
            console.error('Fallimento nella lettura della clipboard:', err);
        });
    }

    selectFolderBtn.addEventListener('click', function() {
        if (window.pywebview) {
            window.pywebview.api.select_folder().then(folder => {
                if (folder) {
                    currentOutputDir = folder;
                    outputPathEl.textContent = formatPath(folder);
                }
            });
        }
    });

    instructionsBtn.addEventListener('click', function() {
        if (window.pywebview) {
            window.pywebview.api.show_instructions();
        } else {
            alert("YTDLPY - How to use:\n\n" +
                "1. Enter the YouTube video URL in the input field.\n" +
                "2. Choose your format preference (MP4 video or MP3 audio).\n" +
                "3. Select the desired quality.\n" +
                "4. Select an output folder (optional).\n" +
                "5. Click the DOWNLOAD button to start downloading.");
        }
    });

    githubLink.addEventListener('click', function(e) {
        e.preventDefault();
        if (window.pywebview) {
            window.pywebview.api.open_url("https://github.com/dddevid/YTDLPY");
        } else {
            window.open("https://github.com/dddevid/YTDLPY", "_blank");
        }
    });

    // Function to open file explorer with downloaded file selected
    function openFileExplorer() {
        if (window.pywebview && downloadedFilePath) {
            window.pywebview.api.open_file_location(downloadedFilePath).then(result => {
                if (!result) {
                    console.error('Failed to open file location');
                }
            });
        }
    }

    // Download function
    downloadBtn.addEventListener('click', function() {
        const url = urlInput.value.trim();
        if (!url) {
            resultStatus.textContent = "Please enter a valid URL";
            resultStatus.classList.add('error');
            setTimeout(() => resultStatus.classList.remove('error'), 3000);
            return;
        }

        // Get selected format
        const formatInputs = document.querySelectorAll('input[name="format"]');
        let selectedFormat;
        formatInputs.forEach(input => {
            if (input.checked) selectedFormat = input.value;
        });

        // Get selected quality
        const qualityInputs = document.querySelectorAll('input[name="quality"]');
        let selectedQuality;
        qualityInputs.forEach(input => {
            if (input.checked) selectedQuality = input.value;
        });

        // Update status and show progress modal
        resultStatus.textContent = "Starting download...";
        progressModal.style.display = "flex";
        modalStatus.textContent = "Downloading...";
        progressFile.textContent = "Preparing download...";
        progressStats.textContent = "";
        progressBar.style.width = "0%";
        progressText.textContent = "0%";
        logText.textContent = "";

        if (window.pywebview) {
            // Call Python API to start download
            window.pywebview.api.start_download(url, selectedFormat, selectedQuality, currentOutputDir)
                .then(response => {
                    console.log("Download response:", response);
                    
                    // Non aggiorniamo qui lo stato, ma lasciamo che le chiamate 
                    // updateProgressUI gestiscano lo stato finale
                    if (response.success) {
                        // Se il download è riuscito, memorizza il percorso del file
                        if (response.filePath) {
                            downloadedFilePath = response.filePath;
                        }
                        // Il messaggio di stato verrà aggiornato dai callback
                    }
                })
                .catch(err => {
                    console.error("Download error:", err);
                    resultStatus.textContent = "Error starting download";
                    modalStatus.textContent = "Download Failed";
                });
        } else {
            // Mock progress for testing in browser
            simulateProgress();
        }
    });

    // Function for testing UI in browser without Python
    function simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 5;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                window.updateProgressUI({
                    status: 'complete',
                    log: 'Download completed successfully!'
                });
            }
            window.updateProgressUI({
                status: 'downloading',
                percent: progress,
                filename: 'Sample Video - Test.mp4',
                speed: `${(Math.random() * 10).toFixed(2)} MB/s`,
                eta: `${Math.round(Math.random() * 10)}:${Math.round(Math.random() * 59).toString().padStart(2, '0')}`,
                log: `Progress update: ${Math.round(progress)}% complete`
            });
        }, 500);
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + V for paste in input field
        if ((e.ctrlKey || e.metaKey) && e.key === 'v' && document.activeElement === urlInput) {
            pasteBtn.click();
        }
        
        // Escape to close modal
        if (e.key === 'Escape' && progressModal.style.display === 'flex') {
            // Only allow closing if download is complete
            if (modalStatus.textContent === 'Download Complete!' || 
                modalStatus.textContent === 'Download Failed' ||
                modalStatus.textContent === 'Error') {
                progressModal.style.display = 'none';
            }
        }
    });

    // Override the updateProgressUI function to handle the explore button
    const originalUpdateProgressUI = window.updateProgressUI;
    window.updateProgressUI = function(data) {
        if (data.status === 'downloading') {
            // Inizializza il tempo di download se non è stato fatto
            if (!downloadStartTime) {
                downloadStartTime = new Date();
                downloadPreviousTime = downloadStartTime;
                downloadPreviousBytes = 0;
            }
            
            // Calcolo velocità e ETA personalizzato
            const currentTime = new Date();
            const currentBytes = data.currentBytes || 0;
            const totalBytes = data.totalBytes || 0;
            
            // Se abbiamo dati sufficienti per calcolare la velocità
            if (currentBytes > 0 && downloadPreviousBytes > 0 && totalBytes > 0) {
                const timeDiff = (currentTime - downloadPreviousTime) / 1000; // in secondi
                
                // Solo se è passato abbastanza tempo per avere un calcolo significativo
                if (timeDiff >= 0.5) {
                    const bytesDiff = currentBytes - downloadPreviousBytes;
                    const speed = bytesDiff / timeDiff; // byte al secondo
                    
                    // Aggiungi la velocità attuale alla storia
                    downloadSpeedHistory.push(speed);
                    if (downloadSpeedHistory.length > MAX_SPEED_HISTORY) {
                        downloadSpeedHistory.shift(); // Rimuovi la velocità più vecchia
                    }
                    
                    // Calcola velocità media
                    const averageSpeed = downloadSpeedHistory.reduce((a, b) => a + b, 0) / downloadSpeedHistory.length;
                    const speedStr = averageSpeed > 1024 * 1024 ? 
                        `${(averageSpeed / (1024 * 1024)).toFixed(2)} MB/s` : 
                        `${(averageSpeed / 1024).toFixed(2)} KB/s`;
                    
                    // Calcola ETA basato sulla velocità media
                    const remainingBytes = totalBytes - currentBytes;
                    if (averageSpeed > 0) {
                        const etaSeconds = remainingBytes / averageSpeed;
                        let etaStr;
                        
                        if (etaSeconds < 60) {
                            etaStr = `${Math.round(etaSeconds)}s`;
                        } else if (etaSeconds < 3600) {
                            const minutes = Math.floor(etaSeconds / 60);
                            const seconds = Math.round(etaSeconds % 60);
                            etaStr = `${minutes}m ${seconds}s`;
                        } else {
                            const hours = Math.floor(etaSeconds / 3600);
                            const minutes = Math.floor((etaSeconds % 3600) / 60);
                            etaStr = `${hours}h ${minutes}m`;
                        }
                        
                        // Aggiorna il data object con le nostre nuove informazioni calcolate
                        data.speed = speedStr;
                        data.eta = etaStr;
                    }
                    
                    // Aggiorna valori per il prossimo calcolo
                    downloadPreviousBytes = currentBytes;
                    downloadPreviousTime = currentTime;
                }
            }
        } else if (data.status === 'complete' || data.status === 'finished') {
            // Resetta le variabili di calcolo per il prossimo download
            downloadStartTime = null;
            downloadPreviousBytes = 0;
            downloadPreviousTime = null;
            downloadSpeedHistory = [];
        }
        
        // Chiama la funzione originale con i dati aggiornati
        originalUpdateProgressUI(data);
        
        // Aggiorna lo stato dell'UI principale in base allo stato del download
        if (data.status === 'complete') {
            // Aggiorna lo stato principale
            resultStatus.textContent = data.title ? 
                `Successfully downloaded: ${data.title}` : 
                "Download completed successfully";
            
            // Aggiorna lo stato del modal
            modalStatus.textContent = "Download Complete!";
            
            // If the file path is provided, store it
            if (data.filePath) {
                downloadedFilePath = data.filePath;
            }
            
            // Add the explore button if it doesn't exist
            if (!document.querySelector('.explore-file-btn') && downloadedFilePath) {
                const modalBody = document.querySelector('.modal-body');
                const existingButtons = document.querySelector('.modal-buttons') || document.createElement('div');
                
                if (!document.querySelector('.modal-buttons')) {
                    existingButtons.className = 'modal-buttons';
                    modalBody.appendChild(existingButtons);
                }
                
                // Create explore button
                const exploreButton = document.createElement('button');
                exploreButton.textContent = 'Esplora file';
                exploreButton.className = 'btn-secondary explore-file-btn';
                exploreButton.style.marginRight = '10px';
                exploreButton.onclick = openFileExplorer;
                
                // Get existing close button or create one
                let closeButton = document.querySelector('.close-btn');
                if (!closeButton) {
                    closeButton = document.createElement('button');
                    closeButton.textContent = 'Chiudi';
                    closeButton.className = 'btn-secondary close-btn';
                    closeButton.onclick = () => progressModal.style.display = 'none';
                } else {
                    // Remove the existing button to reposition it
                    closeButton.remove();
                }
                
                // Clear existing buttons
                existingButtons.innerHTML = '';
                
                // Add buttons in correct order
                existingButtons.appendChild(exploreButton);
                existingButtons.appendChild(closeButton);
                
                // Style the button container
                existingButtons.style.display = 'flex';
                existingButtons.style.justifyContent = 'flex-end';
                existingButtons.style.marginTop = '20px';
                existingButtons.style.gap = '10px';
            }
        }
        else if (data.status === 'error') {
            resultStatus.textContent = "Download failed. See error log for details.";
            modalStatus.textContent = "Download Failed";
        }
    };

    // Initialize
    initializePyWebViewBridge();

    // For demo/testing purposes in browser
    if (!window.pywebview) {
        console.log('PyWebView not detected. Running in test mode.');
    }
});