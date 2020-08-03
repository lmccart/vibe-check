let image_base = 'http://167.172.202.13/images/';
let id = Number(window.location.pathname.substring(1));
let leader_id = 1; // lead screen
let expression;
let photo_width, photo_height, photo_ratio;
let screen_width = window.innerWidth;
let mask_size = 3840;
let mask_zoom = 10.0;
let animation_duration = 5000;
let zoomed_in_pause_duration = 12000;
let zoomed_out_pause_duration = 3000;
let face_x, face_y, start_x;
let blink_interval;

let getMeta = () => {
  $.get('/get_meta', data => {
    console.log(data)
    photo_width = data.photo_width;
    photo_height = data.photo_height;
    photo_ratio = window.innerHeight/photo_height;
    expression = data.expressions[id];
  
    $( '#label' ).css('color', data.colors[id]);
    $( '#expression' ).css('color', data.colors[id]);
    $( '#mask' ).attr('src', '/static/mask-'+expression+'.png');
    
    update(true);
  });  
}
getMeta();

let update = (ready) => {
  $.get('/static/data.json', data => {
    console.log(data[expression]);
    let expression_data = data[expression];
    $('#photo').attr('src', image_base+expression_data.photo_path);
    let label = expression === 'happiness' ? 'glee' : expression;
    $('#expression').text(label);

    let face_w = expression_data.rect[2] * photo_ratio;
    let face_h = expression_data.rect[3] * photo_ratio;
    face_x = expression_data.rect[0] * photo_ratio;
    face_y = expression_data.rect[1] * photo_ratio;
    
    // check which side of photo to start from
    start_x = face_x < photo_width * photo_ratio * 0.5 ? -photo_width * photo_ratio + screen_width : 0;

    if (ready) start();
  });
};

let start = () => {
  reset();
  let totalTime = zoomed_in_pause_duration + zoomed_out_pause_duration + 2 * animation_duration;
  let millis = new Date().getTime();
  let rem = millis % totalTime;
  let diff = totalTime - rem;
  if (diff < 1000) diff += totalTime;
  setTimeout(function() {
    zoomIn();
    zoom_interval = setInterval(zoomIn, totalTime);
  }, diff);
  console.log(diff);
}

// reset photo and mask
let reset = () => {

  blink(false);

  $( '#photo' ).css('height', '100%');
  $( '#photo' ).css('left', start_x);
  $( '#mask' ).css('width', mask_size * mask_zoom);
  $( '#mask' ).css('height', mask_size * mask_zoom);
  $( '#mask' ).css('left', (face_x - mask_size * mask_zoom * 0.5));
  $( '#mask' ).css('top', (face_y - mask_size * mask_zoom * 0.5));
  $( '#label').hide();

  $( '#mask' ).show();
  $( '#photo').stop();
  $( '#mask').stop();
  $( '#label').stop();
  $( '#expression').stop();

};

// slide photo to final position
let slide = (x) => {
  let half = screen_width * 0.5;
  let target_x = half + (Math.random() - 0.5) * screen_width * 0.2;
  let left_diff = photo_width * photo_ratio - x;
  if (target_x > x) target_x = x;
  else if (left_diff < half) target_x = target_x + (half - left_diff);
  let offset = target_x - x;
  $( '#photo' ).delay(zoomed_out_pause_duration).animate({
    left: offset
  }, animation_duration, 'swing');
  return target_x;
}

// zoom into face
let zoomIn = () => {
  blink(true);

  let target_x = slide(face_x);
  $( '#mask' ).delay(zoomed_out_pause_duration).animate({
    width: mask_size,
    height: mask_size,
    left: target_x - mask_size * 0.5,
    top: face_y - mask_size * 0.5,
  }, animation_duration, 'swing', zoomOut);
  
  setTimeout(function() { 
    blink(false);
    $('#label').show();
    $('#expression').css('margin-left', ((Math.random() > 0.5 ? 1 : -1) * 1.8) + 'em');
  }, zoomed_out_pause_duration + animation_duration);
}

// zoom out of face
let zoomOut = () => {
  $( '#photo' ).delay(zoomed_in_pause_duration).animate({
    left: start_x
  }, animation_duration, 'swing');
  $( '#mask' ).delay(zoomed_in_pause_duration).animate({
    width: mask_size * mask_zoom,
    height: mask_size * mask_zoom,
    left: (face_x - mask_size * mask_zoom * 0.5),
    top: (face_y - mask_size * mask_zoom * 0.5)
  }, animation_duration, 'swing');

  setTimeout(function() { 
    blink(true);
    $('#label').hide();
    $('#expression').css('margin-left', 0);
  }, zoomed_in_pause_duration);

  update();
}

let blink = (val) => {
  if (blink_interval) clearInterval(blink_interval);
  if (val) {
    blink_interval = setInterval( function() { 
      if ($( '#expression').css('display') === 'none') 
        $( '#expression').show();
      else
        $( '#expression').hide();
    }, 1000);
  }
};