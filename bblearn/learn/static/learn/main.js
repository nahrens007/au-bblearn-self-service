

function check() {

  isChecked = document.getElementById('checkAll').checked;
  print("working");
  if(isChecked){
    document.getElementsByClassName('userCheckbox').checked = true;
  }

  else {
      document.getElementsByClassName('userCheckbox').checked = false;
  }
}
