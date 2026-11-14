document.querySelectorAll(".flash").forEach((el)=>{setTimeout(()=>{if(el.isConnected)el.remove()},6500)});
document.querySelectorAll('input[type="file"]').forEach((input)=>input.addEventListener("change",()=>{
 const file=input.files && input.files[0];
 if(file && file.size>5*1024*1024){alert("Please choose an image smaller than 5 MB.");input.value="";}
}));
