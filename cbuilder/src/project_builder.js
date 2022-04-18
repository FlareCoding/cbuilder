// Tracker for currently created components
var components = []

function addApplicationComponent() {
    var newComponentName = 'component_' + String(components.length + 1);
    components.push({
        componentName: newComponentName,
        componentClasses: []
    });
    
    var componentCardNameTextbox = document.createElement('input');
    componentCardNameTextbox.classList.add('card-name-textbox');
    componentCardNameTextbox.value = newComponentName;
    componentCardNameTextbox.spellcheck = false;
    componentCardNameTextbox.addEventListener('click', function (e) {
        e.stopPropagation();
    });
    componentCardNameTextbox.addEventListener('keyup', function(e) {
        components[components.length - 1].componentName = e.target.value;
    });

    var componentCardButton = document.createElement('button');
    componentCardButton.classList.add('card-button');
    componentCardButton.role = 'button';
    componentCardButton.appendChild(componentCardNameTextbox);
    componentCardButton.addEventListener('click', function(e) {
        console.log('clicked: ' + e.target.childNodes[0].value);
    });
    componentCardNameTextbox.addEventListener('keypress', function (e) {
        if (e.key === ' ') {
            e.preventDefault();
        }
    });
    componentCardNameTextbox.addEventListener('keyup', function (e) {
        if (e.key === ' ') {
            e.preventDefault();
        }
    });

    var componentCard = document.createElement('div');
    componentCard.classList.add('item-card');
    componentCard.appendChild(componentCardButton);

    var componentsRegion = document.getElementsByClassName('components-region')[0];
    componentsRegion.insertBefore(componentCard, componentsRegion.childNodes[componentsRegion.childNodes.length - 2]);
}