function uploadArtwork(event) {
    event.preventDefault();
    var form = document.getElementById('artworkForm');
    var formData = new FormData(form)

    fetch('/upload_artwork', {
        method: 'POST',
        body: formData, 
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        alert("Artwork uploaded successfully!"); 
        form.reset();
        closeForm();
        updateArtworkList();
    })
    .catch((error) => {
        console.error('Error:', error); 
        alert("Failed to upload artwork."); 
    });
}

function addNewArtworkToDOM(artwork) {
    const artworkList = document.getElementById('artworkList');
    const artContainer = document.createElement('div');
    artContainer.className = 'art-container';
    artContainer.setAttribute('data-id', artwork.id);

    artContainer.innerHTML = `
        <img src="${artwork.image_url}" alt="${artwork.title}">
        <h3>${artwork.title}</h3>
        <p>${artwork.artist}</p>
        <p>Price: $${artwork.price}</p>
        <button class="add-to-cart">Add to Cart</button>
        <button class="delete-artwork" data-id="${artwork.id}">Deleteee</button>
        <button class="edit-artwork" data-artwork-id="${artwork.id}">Edit</button>
        <div class="edit-form" id="edit-form-${artwork.id}" style="display: none;">
            <form method="POST" action="/edit_artwork">
                <input type="hidden" name="artwork_id" value="${artwork.id}">
                <input type="text" name="new_artist" placeholder="New Artist Name">
                <input type="number" name="new_price" placeholder="New Price">
                <button type="submit">Update Artwork</button>
            </form>
        </div>
    `;

    artworkList.insertBefore(artContainer, artworkList.firstChild);
    artContainer.querySelector('.delete-artwork').addEventListener('click', handleDeleteArtwork);
    attachEditButtonListener(artwork.id);
}

function showAddArtworkForm() {
    document.getElementById('addArtworkForm').style.display = 'block';
    document.getElementById('backdrop').style.display = 'block';
    }

function closeForm() {
    document.getElementById('addArtworkForm').style.display='none';
    document.getElementById('backdrop').style.display='none';
}

function updateArtworkList() {
    console.log('Updating artwork list...');
    fetch('/get_artworks')
    .then(response => response.json())
    .then(artworks => {
        console.log('Retrieved artworks:', artworks);
        const artworkList = document.getElementById('artworkList');
        artworkList.innerHTML = ''; 
        artworks.forEach(artwork => {
            const artContainer = document.createElement('div');
            artContainer.className = 'art-container';
            artContainer.innerHTML = `
                <img src="${artwork.image_url}" alt="${artwork.title}" />
                <h3>${artwork.title}</h3>
                <p>${artwork.artist}</p>
                <p>${artwork.price}</p>
                <button>Add to Cart</button>
                <button class="delete-artwork" data-id="${artwork.id}">Delete</button>
                <button class="edit-artwork" data-artwork-id="${artwork.id}">Edit</button>
                <div class="edit-form" id="edit-form-${artwork.id}" style="display: none;">
                    <form method="POST" action="/edit_artwork">
                        <input type="hidden" name="artwork_id" value="${artwork.id}">
                        <input type="text" name="new_artist" placeholder="New Artist Name">
                        <input type="number" name="new_price" placeholder="New Price">
                        <button type="submit">Update Artwork</button>
                    </form>
                </div>
            `;
            artworkList.appendChild(artContainer);
            artContainer.querySelector('.delete-artwork').addEventListener('click', handleDeleteArtwork)
            attachEditButtonListener(artwork.id);
        });
    })
    .catch(error => {
        console.error('Error fetching artworks:', error);
    });
}

function attachEditButtonListener(artworkId) {
    const editButton = document.querySelector(`.edit-artwork[data-artwork-id='${artworkId}']`);
    const editForm = document.getElementById(`edit-form-${artworkId}`);

    if (editButton && editForm) {
        editButton.addEventListener('click', function() {
            editForm.style.display = 'block';
        });
    }
}

function handleDeleteArtwork(event) {
    const artworkId = this.dataset.id;
    const confirmation = confirm('Are you sure you want to delete this artwork?');
    if (confirmation) {
        deleteArtwork(artworkId);
    }
}

function deleteArtwork(artworkId) {
    console.log('Deleting artwork with ID:', artworkId);
    fetch('/delete_artwork/' + artworkId, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Artwork deleted successfully');
            updateArtworkList();
        } else {
            alert('There was an error deleting the artwork');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

document.getElementById('artworkForm').addEventListener('submit', uploadArtwork);

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('artworkForm');
    if (form) {
      form.addEventListener('submit', uploadArtwork);
    } else {
      console.error('The form with ID "artworkForm" was not found on the page.');
    }
    updateArtworkList();
});

document.getElementById('homeLink').addEventListener('click', function(event) {
    event.preventDefault();
    resetToHome();
});

function resetToHome() {
    document.getElementById('artworkList').innerHTML = '';
    updateArtworkList();
}


document.getElementById('generateStatsLink').addEventListener('click', function(event) {
    event.preventDefault();
    fetchStatisticsContent();
});

function fetchStatisticsContent() {
    fetch('/statistics_content')
    .then(response => response.json())
    .then(data => {
        document.getElementById('artworkList').innerHTML = data.htmlContent;
    })
    .catch(error => console.error('Error fetching statistics:', error));
}
