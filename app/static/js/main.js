let imageBase = 'http://167.172.202.13/images/';
let id = Number(window.location.pathname.substring(1));
let expression;

$.get('/get_expressions', data => {
  expression = data[id];
  console.log(id, expression);
  setInterval(update, 3000);
});

let update = () => {
  console.log(update);
  $.get('/static/data.json', data => {
    let expressionData = data[expression];
    $('#photo').attr('src', imageBase+expressionData.photoPath);
    $('#expression').text(expression);
  });
};
