
let player = document.getElementById('playback')

var rows1 = document.getElementsByName("1");
rows1.forEach(row => row.style = "background:lavenderblush");

var rows2 = document.getElementsByName("2");
rows2.forEach(row => row.style = "background:cornsilk");

var rows3 = document.getElementsByName("3");
rows3.forEach(row => row.style = "background:honeydew");



function playAudio(current) {
    player.src = current.value   
}

function setVocab(current) {
  $.ajax({
			data : {
                state : current.value,
                vocab : current.name
			},
			type : 'POST',
      url : '/update', 
           
		})
		.done(function(data) {  
      colors = ['pink', 'red', 'yellow', 'green']           
            if (data.state == 1) {                                
               document.getElementById(data.vocab + 'card').style = "background:lavenderblush"
            }
            else if (data.state == 2) {                                
               document.getElementById(data.vocab + 'card').style = "background:cornsilk"
            }
            else if (data.state == 3) {                                
               document.getElementById(data.vocab + 'card').style = "background:honeydew"         
            }
		});
    
}