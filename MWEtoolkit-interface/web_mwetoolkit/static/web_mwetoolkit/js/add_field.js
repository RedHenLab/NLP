/**
 * Created by Sereni on 6/3/15.
 */

//get button reference
var addBtn = document.getElementById('addField');

//add click function
addBtn.addEventListener('click', function(event) {
  addField();
});

//it's more efficient to get the form reference outside of the function, rather than getting it each time
var form = document.getElementById('constructor');

function addField() {
  var input = document.createElement('input');
  var form = document.getElementById('constructor');

  form.appendChild(input);
}