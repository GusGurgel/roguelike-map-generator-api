// Configurações do Tileset (Ajuste conforme o arquivo tileset.png real)
const TILE_SIZE = 16;      // Tamanho do tile em pixels (16x16)
const TILE_SPACING = 0;    // Espaço entre tiles no arquivo (Kenny Pack costuma ter 1px)
const SCALE_FACTOR = 3;    // Fator de escala para visualização (3x maior = 48px)

const tilesetImage = new Image();
let isTilesetLoaded = false;

// 1. Carregar a imagem tileset.png
tilesetImage.src = 'tileset.png';
tilesetImage.onload = () => {
    isTilesetLoaded = true;
    updateStatus("Tileset carregado! Aguardando JSON.");
    console.log("Tileset loaded successfully.");
};
tilesetImage.onerror = () => {
    updateStatus("Erro ao carregar 'tileset.png'. Verifique se o arquivo está na pasta.");
};

// 2. Referências de DOM
const fileInput = document.getElementById('fileInput');
const btnSave = document.getElementById('btnSave');
const statusMsg = document.getElementById('statusMsg');

// 3. Listener do Arquivo JSON
fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!isTilesetLoaded) {
        alert("A imagem tileset.png ainda não carregou ou não foi encontrada.");
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const json = JSON.parse(e.target.result);
            renderAssetBundle(json);
            btnSave.disabled = false;
            updateStatus("JSON processado com sucesso.");
        } catch (error) {
            console.error(error);
            alert("Erro ao ler o JSON. Verifique o console.");
        }
    };
    reader.readAsText(file);
});

// 4. Salvar Imagem (html2canvas)
btnSave.addEventListener('click', () => {
    const captureArea = document.getElementById('capture-area');
    
    html2canvas(captureArea, {
        backgroundColor: "#1e1e1e", // Cor de fundo da imagem salva
        scale: 2 // Alta resolução
    }).then(canvas => {
        const link = document.createElement('a');
        link.download = 'asset_bundle_view.png';
        link.href = canvas.toDataURL();
        link.click();
    });
});

function updateStatus(msg) {
    statusMsg.textContent = msg;
}

// 5. Função Utilitária: Snake Case -> Title Case
function snakeToTitle(str) {
    if (!str) return "";
    return str.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// 6. Função Core: Desenhar Tile Colorido
function createTileCanvas(tileData) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Tamanho final no canvas (escalado)
    const size = TILE_SIZE * SCALE_FACTOR;
    canvas.width = size;
    canvas.height = size;

    // Dados do JSON
    // O modelo pode estar aninhado em "tile_with_texture" ou direto
    const textureData = tileData.texture || (tileData.tile_with_texture && tileData.tile_with_texture.texture);
    const colorHex = tileData.color || (tileData.tile_with_texture && tileData.tile_with_texture.color) || "#ffffff";
    
    if (!textureData) {
        console.warn("No texture data for", tileData);
        return canvas; // Retorna vazio
    }

    const tx = textureData.tileset_position.x;
    const ty = textureData.tileset_position.y;

    // Calcular posição exata no tileset.png
    // Fórmula: (Index * (Tamanho + Espaço))
    const srcX = tx * (TILE_SIZE + TILE_SPACING);
    const srcY = ty * (TILE_SIZE + TILE_SPACING);

    // Configurar desenho pixelado
    ctx.imageSmoothingEnabled = false;

    // --- Passo A: Desenhar o sprite original ---
    // Desenhamos na escala final
    ctx.drawImage(
        tilesetImage,
        srcX, srcY, TILE_SIZE, TILE_SIZE, // Fonte
        0, 0, size, size                  // Destino
    );

    // --- Passo B: Colorir (Tint) ---
    // 'source-in' mantém o novo desenho (retângulo de cor) apenas onde
    // já existem pixels não-transparentes no canvas.
    ctx.globalCompositeOperation = 'source-in';
    ctx.fillStyle = colorHex;
    ctx.fillRect(0, 0, size, size);

    // Resetar composição (boa prática)
    ctx.globalCompositeOperation = 'source-over';

    canvas.classList.add('tile-canvas');
    return canvas;
}

// 7. Função Principal de Renderização
function renderAssetBundle(data) {
    // Mostrar containers
    document.getElementById('bundle-header').classList.remove('hidden');
    document.getElementById('content-grid').classList.remove('hidden');

    // --- Header ---
    document.getElementById('bundle-title').innerText = data.name || "Sem Nome";
    document.getElementById('bundle-desc').innerText = data.description || "";
    document.getElementById('gen-time').innerText = data.generation_time_seconds || 0;

    // --- Player ---
    const playerContainer = document.getElementById('player-container');
    playerContainer.innerHTML = '';
    if (data.player && data.player.tile_with_texture) {
        const pData = data.player.tile_with_texture;
        const card = document.createElement('div');
        card.className = 'item-card';
        
        card.appendChild(createTileCanvas(pData));
        
        const info = document.createElement('div');
        info.className = 'item-info';
        info.innerHTML = `<h3>${snakeToTitle(pData.name)}</h3>`;
        card.appendChild(info);

        playerContainer.appendChild(card);
    }

    // --- Final Objective ---
    const objContainer = document.getElementById('objective-container');
    objContainer.innerHTML = '';
    if (data.final_objective && data.final_objective.tile_with_texture) {
        const objData = data.final_objective.tile_with_texture;
        const card = document.createElement('div');
        card.className = 'item-card';
        
        card.appendChild(createTileCanvas(objData));
        
        const info = document.createElement('div');
        info.className = 'item-info';
        info.innerHTML = `<h3>${snakeToTitle(objData.name)}</h3>`;
        card.appendChild(info);

        objContainer.appendChild(card);
    }

    // --- Levels ---
    const levelsList = document.getElementById('levels-list');
    levelsList.innerHTML = '';
    if (data.dungeon_levels && data.dungeon_levels.items) {
        data.dungeon_levels.items.forEach(lvl => {
            const row = document.createElement('div');
            row.className = 'level-row';

            // Nome Nível
            const nameDiv = document.createElement('div');
            nameDiv.innerHTML = `<strong>${lvl.name}</strong><br><small>Depth: ${lvl.depth}</small>`;
            row.appendChild(nameDiv);

            // Wall
            const wallDiv = document.createElement('div');
            wallDiv.className = 'mini-tile';
            wallDiv.innerHTML = '<span>Wall:</span>';
            if(lvl.wall_tile_with_texture) {
                // Criar versão menor do canvas para lista
                const cvs = createTileCanvas(lvl.wall_tile_with_texture);
                cvs.style.width = '32px'; cvs.style.height = '32px'; // Override css
                wallDiv.appendChild(cvs);
                // wallDiv.innerHTML += ` <small>${snakeToTitle(lvl.wall_tile_with_texture.name)}</small>`;
            }
            row.appendChild(wallDiv);

            // Floor
            const floorDiv = document.createElement('div');
            floorDiv.className = 'mini-tile';
            floorDiv.innerHTML = '<span>Floor:</span>';
            if(lvl.floor_tile_with_texture) {
                const cvs = createTileCanvas(lvl.floor_tile_with_texture);
                cvs.style.width = '32px'; cvs.style.height = '32px';
                floorDiv.appendChild(cvs);
                // floorDiv.innerHTML += ` <small>${snakeToTitle(lvl.floor_tile_with_texture.name)}</small>`;
            }
            row.appendChild(floorDiv);

            levelsList.appendChild(row);
        });
    }

    // --- Helper Generico para Listas de Itens ---
    const renderList = (items, containerId) => {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        if (!items) return;

        items.forEach(item => {
            const tileData = item.tile_with_texture;
            if (!tileData) return;

            const card = document.createElement('div');
            card.className = 'item-card vertical'; // Vertical layout for grid

            card.appendChild(createTileCanvas(tileData));

            const info = document.createElement('div');
            info.className = 'item-info';
            info.innerHTML = `<h3>${snakeToTitle(tileData.name)}</h3>`;
            
            // Adicionar detalhes extras se for arma ou inimigo
            if(item.rarity !== undefined) info.innerHTML += `<span>Rarity: ${item.rarity}</span>`;
            if(item.thread !== undefined) info.innerHTML += `<span>Threat: ${item.thread}</span>`;

            card.appendChild(info);
            container.appendChild(card);
        });
    };

    // --- Enemies ---
    if (data.enemies && data.enemies.items) {
        renderList(data.enemies.items, 'enemies-list');
    }

    // --- Weapons ---
    if (data.weapons && data.weapons.items) {
        renderList(data.weapons.items, 'weapons-list');
    }
}