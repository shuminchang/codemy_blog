CKEDITOR.on('instanceReady', function(event) {
    var editor = event.editor;

    editor.on('fileUploadRequest', function(evt) {
        var xhr = evt.data.fileLoader.xhr;
        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
    });

    // Add listener for drag and drop
    editor.on('drop', function(evt) {
        var dataTransfer = evt.data.$.dataTransfer;
        if (dataTransfer && dataTransfer.files) {
            Array.from(dataTransfer.files).forEach(file => {
                if (file.type.startsWith('image/')) {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        var img = new Image();
                        img.src = e.target.result;
                        img.onload = function() {
                            var canvas = document.createElement('canvas');
                            var ctx = canvas.getContext('2d');
                            var maxWidth = 800;
                            var maxHeight = 600;
                            var targetWidth, targetHeight;

                            // Determine new size while maintaining aspect ratio
                            if (img.width > img.height) {
                                // Horizontal image
                                targetWidth = maxWidth;
                                targetHeight = Math.round(maxWidth * img.height / img.width);
                            } else {
                                // Vertical image
                                targetHeight = maxHeight;
                                targetWidth = Math.round(maxHeight * img.width / img.height);
                            }

                            canvas.width = targetWidth;
                            canvas.height = targetHeight;
                            ctx.drawImage(img, 0, 0, targetWidth, targetHeight);

                            var resizedDataUrl = canvas.toDataURL('image/jpeg', 0.85);
                            editor.insertHtml('<img src="' + resizedDataUrl + '" width="' + targetWidth + '" height="' + targetHeight + '"/>');
                        };
                    };
                    reader.readAsDataURL(file);
                }
            });
            evt.stop();
        }
    });
});
