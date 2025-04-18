document.addEventListener('DOMContentLoaded', async function () {
    let materias = [];
    let grafoData = null;

    initTabs();

    await loadInitialData();

    setupCalculateButton();

    function initTabs() {
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', function () {
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });

                this.classList.add('active');

                const tabId = this.getAttribute('data-tab');
                const contentElement = document.getElementById(`${tabId}-container`);
                if (contentElement) {
                    contentElement.classList.add('active');
                }

                switch (tabId) {
                    case 'cadeias':
                        if (grafoData) {
                            renderCadeias(grafoData.cadeias, grafoData.cursadas);
                        }
                        break;
                    case 'recomendacoes':
                        if (grafoData) {
                            renderRecomendacoes(grafoData.recomendacoes);
                        }
                        break;
                }
            });
        });
    }

    async function loadInitialData() {
        try {
            const response = await fetch('data.json');
            if (!response.ok) throw new Error('Falha ao carregar dados');
            materias = await response.json();
            renderMaterias(materias);
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            showError('Erro ao carregar os dados das matérias');
        }
    }

    function setupCalculateButton() {
        const button = document.getElementById('calcular-btn');
        button.addEventListener('click', async function () {
            const semestreAtual = parseInt(document.getElementById('semestre-atual').value);
            const materiasCursadas = getMateriasCursadas();

            if (materiasCursadas.length === 0) {
                showError('Selecione pelo menos uma matéria cursada');
                return;
            }

            try {
                setButtonState(button, 'loading');

                const response = await fetch('http://localhost:8000/processar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        materias: materias,
                        cursadas: materiasCursadas,
                        semestreAtual: semestreAtual
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Erro desconhecido no servidor');
                }

                const resultado = await response.json();

                if (!resultado.recomendacoes || !resultado.cadeias) {
                    throw new Error('Resposta do servidor em formato inválido');
                }

                grafoData = {
                    recomendacoes: resultado.recomendacoes,
                    cadeias: resultado.cadeias,
                    cursadas: materiasCursadas
                };

                renderRecomendacoes(resultado.recomendacoes);
                renderCadeias(resultado.cadeias, materiasCursadas);

                document.querySelector('.tab-button[data-tab="recomendacoes"]').click();

                setButtonState(button, 'success');
                setTimeout(() => setButtonState(button, 'default'), 2000);

            } catch (error) {
                console.error('Erro ao processar:', error);
                showError('Erro ao processar: ' + error.message);
                setButtonState(button, 'error');
                setTimeout(() => setButtonState(button, 'default'), 2000);
            }
        });
    }

    function renderMaterias(materias) {
        const container = document.getElementById('materias-container');
        container.innerHTML = '';

        materias.forEach(materia => {
            const materiaItem = document.createElement('div');
            materiaItem.className = 'materia-item';
            materiaItem.innerHTML = `
                <input type="checkbox" id="materia-${materia.sigla}" value="${materia.sigla}">
                <label for="materia-${materia.sigla}">
                    <span class="materia-sigla"><strong>${materia.sigla}</strong> - </span>
                    <span class="materia-nome">${materia.nome}</span>
                </label>
            `;
            container.appendChild(materiaItem);
        });
    }

    function renderRecomendacoes(recomendacoes) {
        const container = document.getElementById('recomendacoes-container');
        container.innerHTML = '';

        if (!recomendacoes || typeof recomendacoes !== 'object') {
            container.innerHTML = '<div class="no-results">Nenhuma recomendação disponível</div>';
            return;
        }

        Object.entries(recomendacoes).forEach(([semestre, materias]) => {
            const semestreBox = document.createElement('div');
            semestreBox.className = 'semestre-box';

            const semestreTitle = document.createElement('div');
            semestreTitle.className = 'semestre-title';
            semestreTitle.innerHTML = `
                <span class="semestre-text">${semestre}</span>
            `;

            const materiaList = document.createElement('div');
            materiaList.className = 'materia-list';

            if (Array.isArray(materias)) {
                materias.forEach(materia => {
                    const materiaChip = document.createElement('div');
                    materiaChip.className = 'materia-chip';
                    materiaChip.textContent = materia;
                    materiaList.appendChild(materiaChip);
                });
            } else {
                materiaList.innerHTML = '<div class="no-materias">Nenhuma matéria recomendada</div>';
            }

            semestreBox.appendChild(semestreTitle);
            semestreBox.appendChild(materiaList);
            container.appendChild(semestreBox);
        });
    }

    function renderCadeias(cadeias, cursadas) {
        const container = document.getElementById('cadeias-container');
        container.innerHTML = '';

        if (!Array.isArray(cadeias)) {
            container.innerHTML = '<div class="no-results">Nenhuma cadeia de pré-requisitos disponível</div>';
            return;
        }

        cadeias.forEach(cadeia => {
            if (!Array.isArray(cadeia) || cadeia.length < 2) return;

            const cadeiaItem = document.createElement('div');
            cadeiaItem.className = 'cadeia-item';

            let html = '';
            cadeia.forEach((materia, index) => {
                const isCursada = cursadas.includes(materia);
                const classe = isCursada ? 'materia-cursada' : 'materia-pendente';

                html += `<span class="${classe}">${materia}</span>`;
                if (index < cadeia.length - 1) {
                    html += ' <span class="arrow">→</span> ';
                }
            });

            cadeiaItem.innerHTML = html;
            container.appendChild(cadeiaItem);
        });
    }

    function getMateriasCursadas() {
        const checkboxes = document.querySelectorAll('#materias-container input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    function showError(message) {
        const existingError = document.querySelector('.error-message.global');
        if (existingError) existingError.remove();

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message global';
        errorDiv.innerHTML = `
            <span class="error-icon">⚠️</span>
            <span class="error-text">${message}</span>
        `;

        document.body.appendChild(errorDiv);
        setTimeout(() => {
            errorDiv.classList.add('fade-out');
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }

    function setButtonState(button, state) {
        const states = {
            'default': {
                text: 'Gerar Recomendações',
                icon: '→',
                class: ''
            },
            'loading': {
                text: 'Processando...',
                icon: '⌛',
                class: 'loading'
            },
            'success': {
                text: 'Recomendações Geradas!',
                icon: '✓',
                class: 'success'
            },
            'error': {
                text: 'Tentar Novamente',
                icon: '↻',
                class: 'error'
            }
        };

        button.innerHTML = `
            <span class="button-text">${states[state].text}</span>
            <span class="button-icon">${states[state].icon}</span>
        `;
        button.className = `primary-button ${states[state].class}`;
        button.disabled = state === 'loading';
    }
});

