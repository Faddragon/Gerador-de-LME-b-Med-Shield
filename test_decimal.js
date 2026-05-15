let s = '0,25 mcg - cpsula';
let p = s.replace(/(\d),(\d)/g, '$1DECIMAL$2');
console.log('Protegido:', p);

let arr = p.split(',').map(d => d.trim()).filter(d => d);
console.log('Separado:', arr);

arr = arr.map(d => d.replace(/(\d)DECIMAL(\d)/g, '$1,$2'));
console.log('Restaurado:', arr);