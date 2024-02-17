image_extension_dict = {
    'jpg': 1,
    'jpeg': 1,
    'png': 1,
    'gif': 1,
    'bmp': 1,
    'webp': 1,
    'svg': 1,
    'tiff': 1,
    'ico': 1,
    'jpe': 1,
    'jfif': 1,
    'pjpeg': 1,
    'pjp': 1,
    'avif': 1,
    'apng': 1
}


function clickImage(img) {
    var displayedImage = document.getElementById('displayed-image');
    var imageId = getImageId(img.id);
    if (imageId == NaN) {
        return;
    }

    var curr = img.id;
    var prev = imageId == 0 ? null : 'image-grid-' + String(imageId - 1);
    var next = document.getElementById('image-grid-' + String(imageId + 1)) ? 'image-grid-' + String(imageId + 1) : null;
    var imageFilename = img.src.split('/').pop();

    if (isImage(img.src)) {
        displayedImage.src = img.src;
    } else {
        displayedImage.src = "/static/images/broken_image.png";
    }
    displayedImage.setAttribute("imageId", curr);
    adjustSize(displayedImage);

    $("#fullscreen-overlay").fadeIn(200);
    displayedImage.hidden = false;
    document.getElementById('image-display').hidden = false;
    $('#image-filename').text(imageFilename);
    document.getElementById('image-navigation-buttons').hidden = false;
    document.getElementById('previous-image-button').setAttribute("prev", prev);
    document.getElementById('previous-image-button').disabled = !prev;
    document.getElementById('next-image-button').setAttribute("next", next);
    document.getElementById('next-image-button').disabled = !next;
}

function closeImage() {
    $("#fullscreen-overlay").fadeOut();
    document.getElementById('image-display').hidden = true;
    $('#image-filename').text('');
    document.getElementById('image-navigation-buttons').hidden = true;
    document.getElementById('previous-image-button').setAttribute("prev", null);
    document.getElementById('next-image-button').setAttribute("next", null);
}

function nextImage(button) {
    if (!button.getAttribute("next")) {
        return;
    }

    var displayedImage = document.getElementById('displayed-image');
    // The "displayed-image" also has an "imageId" in "image-grid-ID" format, the ID for current displayed image
    var currId = getImageId(displayedImage.getAttribute("imageId"));
    if (currId == NaN) {
        return;
    }

    var curr = button.getAttribute("next");
    var prev = 'image-grid-' + String(currId);
    var next = document.getElementById('image-grid-' + String(currId + 2)) ? 'image-grid-' + String(currId + 2) : null;
    var imageFilename = document.getElementById(curr).src.split('/').pop();

    if (isImage(document.getElementById(curr).src)) {
        displayedImage.src = document.getElementById(curr).src;
    } else {
        displayedImage.src = "/static/images/broken_image.png";
    }
    displayedImage.setAttribute("imageId", curr);
    adjustSize(displayedImage);
    displayedImage.hidden = false;
    document.getElementById('image-display').hidden = false;
    $('#image-filename').text(imageFilename);
    document.getElementById('image-navigation-buttons').hidden = false;
    document.getElementById('previous-image-button').setAttribute("prev", prev);
    document.getElementById('previous-image-button').disabled = !prev;
    document.getElementById('next-image-button').setAttribute("next", next);
    document.getElementById('next-image-button').disabled = !next;
}

function previousImage(button) {
    if (!button.getAttribute("prev")) {
        return;
    }

    var displayedImage = document.getElementById('displayed-image');
    // The "displayed-image" has an "imageId" in "image-grid-ID" format, the ID for current displayed image
    var currId = getImageId(displayedImage.getAttribute("imageId"));
    if (currId == NaN) {
        return;
    }

    var curr = button.getAttribute("prev");
    var prev = document.getElementById('image-grid-' + String(currId - 2)) ? 'image-grid-' + String(currId - 2) : null
    var next = 'image-grid-' + String(currId);
    var imageFilename = document.getElementById(curr).src.split('/').pop();

    if (isImage(document.getElementById(curr).src)) {
        displayedImage.src = document.getElementById(curr).src;
    } else {
        displayedImage.src = "/static/images/broken_image.png";
    }
    displayedImage.setAttribute("imageId", curr);
    adjustSize(displayedImage);
    displayedImage.hidden = false;
    document.getElementById('image-display').hidden = false;
    $('#image-filename').text(imageFilename);
    document.getElementById('image-navigation-buttons').hidden = false;
    document.getElementById('previous-image-button').setAttribute("prev", prev);
    document.getElementById('previous-image-button').disabled = !prev;
    document.getElementById('next-image-button').setAttribute("next", next);
    document.getElementById('next-image-button').disabled = !next;
}

function adjustSize(displayedImage) {
    imageRatio = displayedImage.naturalWidth / displayedImage.naturalHeight
    isSquareIsh = imageRatio > 0.9 && imageRatio < 1.1;

    // For small images, use the image's natural size
    if (displayedImage.naturalWidth < screen.width * 0.6 && displayedImage.naturalHeight < screen.height * 0.6) {
        displayedImage.width = displayedImage.naturalWidth;
        displayedImage.height = displayedImage.naturalHeight;
        return
    }

    // Large images are scaled down to fit the screen
    if (isSquareIsh) {
        // For square-ish images, use 70% of the screen height
        displayedImage.width = imageRatio * screen.height * 0.70;
        displayedImage.height = screen.height * 0.70;
    }
    else if (imageRatio > 1) {
        // For landscape images, use 75% of the screen width
        displayedImage.width = screen.width * 0.75;
        displayedImage.height = screen.width * 0.75 / imageRatio;
        // If the image is still too big, scale it down again
        if (displayedImage.height > screen.height * 0.8) {
            displayedImage.width = screen.width * 0.65;
            displayedImage.height = screen.width * 0.65 / imageRatio;
        }
    } else {
        // For portrait images, use 80% of the screen height
        displayedImage.width = imageRatio * screen.height * 0.80;
        displayedImage.height = screen.height * 0.80;
    }
}

function getImageId(imageId) {
    try {
        // <img> tag's id is in "image-grid-ID" format
        if (imageId === null || imageId === undefined || imageId === "" || imageId === NaN) {
            return NaN;
        }
        var imageIndexInt = Number(imageId.split('-')[2]);  // Ensure imageIndex is a number
        if (imageIndexInt == NaN) {
            return NaN;
        }
        return imageIndexInt;
    }
    catch (err) {
        return NaN;
    }
}

function isImage(filename) {
    var extension = filename.split('.').pop().toLowerCase();
    return image_extension_dict[extension] === 1;
}
