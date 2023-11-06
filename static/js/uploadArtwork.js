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
        <p>${artwork.artist}</p> <!-- Adjust according to your data structure -->
        <p>Price: $${artwork.price}</p>
        <button class="add-to-cart">Add to Cart</button>
        <button class="delete-artwork" data-id="${artwork.id}">Delete</button>
    `;

    artworkList.insertBefore(artContainer, artworkList.firstChild);
    artContainer.querySelector('.delete-artwork').addEventListener('click', handleDeleteArtwork);
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
            `;
            artworkList.appendChild(artContainer);
            artContainer.querySelector('.delete-artwork').addEventListener('click', handleDeleteArtwork)
        });
    })
    .catch(error => {
        console.error('Error fetching artworks:', error);
    });
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