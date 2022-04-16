// Tracker for currently created components
var components = []

function addApplicationComponent() {
    var newComponentName = 'component_' + String(components.length);
    components.push(newComponentName);
    
    var componentCardButton = document.createElement('button');
    componentCardButton.classList.add('card-button');
    componentCardButton.role = 'button';
    componentCardButton.innerHTML = newComponentName;

    var componentCard = document.createElement('div');
    componentCard.classList.add('item-card');
    componentCard.appendChild(componentCardButton);

    var componentsRegion = document.getElementsByClassName('components-region')[0];
    componentsRegion.insertBefore(componentCard, componentsRegion.childNodes[componentsRegion.childNodes.length - 2]);
}