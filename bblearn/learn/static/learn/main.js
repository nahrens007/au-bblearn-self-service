

function check() {

  isChecked = document.getElementById('checkAll').checked;
  print("working");
  if(isChecked){
    for (var i = 0; i < array.length; i++) {
      document.getElementById('userCheckbox' + i).checked = true;
    }

  }

  else {
    for (var i = 0; i < array.length; i++) {
      document.getElementById('userCheckbox' + i).checked = false;
    }
  }
}
