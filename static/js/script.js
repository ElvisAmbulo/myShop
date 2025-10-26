
    // gallery thumbnail click -> main image
    document.querySelectorAll('.thumb').forEach(t => {
      t.addEventListener('click', () => {
        document.querySelectorAll('.thumb').forEach(x=>x.classList.remove('active'));
        t.classList.add('active');
        const src = t.getAttribute('data-src');
        document.getElementById('mainImage').src = src;
      });
    });

    // qty inc/dec
    const qtyVal = document.getElementById('qtyVal');
    document.getElementById('incQty').addEventListener('click', ()=> { qtyVal.innerText = parseInt(qtyVal.innerText) + 1;});
    document.getElementById('decQty').addEventListener('click', ()=> { if(parseInt(qtyVal.innerText)>1) qtyVal.innerText = parseInt(qtyVal.innerText) - 1;});

    // tabs
    document.querySelectorAll('.tab-buttons button').forEach(btn=>{
      btn.addEventListener('click', ()=>{
        document.querySelectorAll('.tab-buttons button').forEach(b=>b.classList.remove('active'));
        btn.classList.add('active');
        const tab = btn.getAttribute('data-tab');
        document.querySelectorAll('.tab-content').forEach(tc=>tc.style.display='none');
        document.getElementById(tab).style.display='block';
      });
    });

    // variant active toggle
    document.querySelectorAll('.variants button').forEach(b=>{
      b.addEventListener('click', ()=> {
        document.querySelectorAll('.variants button').forEach(x=>x.classList.remove('active'));
        b.classList.add('active');
      })
    });
  

    // profile pic change
    function previewImage(event) {
      const preview = document.getElementById('preview');
      const file = event.target.files[0];
      if (file) {
        preview.src = URL.createObjectURL(file);
      }
    }
