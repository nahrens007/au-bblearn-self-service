
document.getElementById('searchOptions').selectedIndex ={{ optionIndex | safe}};

function check() {
  var x = document.getElementsByClassName('userCheckbox');
  isChecked = document.getElementById('checkAll').checked;

  if(isChecked){
    for (var i = 0; i < x.length; i++) {
      x[i].checked = true;
    }

  }

  else {
    for (var i = 0; i < x.length; i++) {
      x[i].checked = false;
    }
  }
}
