let image_base = './images/';
let id = Number(window.location.pathname.substring(1));
let expression, label;
let photo_width, photo_height, photo_ratio;
let screen_width = window.innerWidth;
let screen_height = window.innerHeight;
let mask_size = 3840;
let mask_zoom = 10.0;

let rush_debug = true;
let speed = 1;
let animation_duration = 3000 / speed;
let zoomed_in_pause_duration = 4000 / speed;
let zoomed_out_pause_duration = 4000 / speed;
let mask_zoom_duration = 1000 / speed;
let stored_face_x, stored_face_y, stored_start_x;
let blink_interval;
let screen_off = id * 100 / speed;

let getConfig = () => {
  $.get('/static/config.json', data => {
    console.log(data)
    photo_ratio = screen_height/data.photo_height;
    photo_width = data.photo_width * photo_ratio;
    photo_height = data.photo_height * photo_ratio;
    expression = data.expressions[id].expression;
    label = data.expressions[id].label;
  
    $( '#label' ).css('color', data.expressions[id].color);
    $( '#expression' ).css('color', data.expressions[id].color);
    $( '#mask' ).attr('src', '/static/mask-'+expression+'.png');
    
    update(true);
  });  
}
getConfig();

let update = (ready) => {
  $.get('/static/data.json', data => {
    console.log(data[expression]);
    let expression_data = data[expression];
    let url = image_base+expression_data.photo_path;
    if (url !== $('#photo').attr('src')) {
      $('#photo').attr('src', url);
      console.log('change!');
    }
    $('#expression').text(label);

    let face_w = expression_data.rect[2] * photo_ratio;
    let face_h = expression_data.rect[3] * photo_ratio;
    stored_face_x = expression_data.rect[0] * photo_ratio;
    stored_face_y = expression_data.rect[1] * photo_ratio;
    
    // check which side of photo to start from
    stored_start_x = stored_face_x < photo_width * 0.5 ? -photo_width + screen_width : 0;

    if (ready) start();
  });
};

let start = () => {
  
  // reset
  blink(false);
  $( '#photo' ).css('height', '100%');
  $( '#photo' ).css('left', stored_start_x);
  $( '#mask' ).css('width', mask_size * mask_zoom);
  $( '#mask' ).css('height', mask_size * mask_zoom);
  $( '#mask' ).css('left', (stored_face_x - mask_size * mask_zoom * 0.5));
  $( '#mask' ).css('top', (stored_face_y - mask_size * mask_zoom * 0.5));
  $( '#label').hide();

  $( '#mask' ).show();
  $( '#photo').stop();
  $( '#mask').stop();
  $( '#label').stop();
  $( '#expression').stop();


  let totalTime = zoomed_in_pause_duration + zoomed_out_pause_duration + 2 * animation_duration;
  let millis = new Date().getTime();
  let rem = millis % totalTime;
  let diff = totalTime - rem + screen_off;
  if (diff < 1000) diff += totalTime;
  if (rush_debug) diff = 500;
  setTimeout(function() {
    zoomIn();
    zoom_interval = setInterval(zoomIn, totalTime);
  }, diff);
  console.log(diff);
}

// slide photo to final position
let slide = (x) => {
  let half = screen_width * 0.5;
  let target_x = half + (Math.random() - 0.5) * screen_width * 0.2;
  let left_diff = photo_width - x;
  if (target_x > x) target_x = x;
  else if (left_diff < half) target_x = target_x + (half - left_diff);
  let offset = target_x - x;
  // console.log(offset, screen_width - photo_width)
  offset = Math.max(offset, screen_width - photo_width);
  offset = Math.min(offset, 0);
  $( '#photo' ).delay(zoomed_out_pause_duration).animate({
    left: offset
  }, animation_duration, 'swing');
  return target_x;
}

// zoom into face
let zoomIn = () => {
  update();
  blink(true);

  let target_x = slide(stored_face_x);
  $( '#mask' ).delay(zoomed_out_pause_duration + animation_duration - mask_zoom_duration).animate({
    width: mask_size,
    height: mask_size,
    left: target_x - mask_size * 0.5,
    top: stored_face_y - mask_size * 0.5,
  }, mask_zoom_duration, 'swing', function() { zoomOut(stored_face_x, stored_face_y, stored_start_x); });
  
  setTimeout(function() { 
    blink(false);
    $('#label').show();
    $('#expression').css('margin-left', ((Math.random() > 0.5 ? 1 : -1) * 1.8) + 'em');
    $('#expression').show();
  }, zoomed_out_pause_duration + animation_duration);
}

// zoom out of face
let zoomOut = (face_x, face_y, start_x) => {
  $( '#photo' ).delay(zoomed_in_pause_duration - screen_off).animate({
    left: start_x
  }, animation_duration, 'swing');
  $( '#mask' ).delay(zoomed_in_pause_duration - screen_off).animate({
    width: mask_size * mask_zoom,
    height: mask_size * mask_zoom,
    left: (face_x - mask_size * mask_zoom * 0.5),
    top: (face_y - mask_size * mask_zoom * 0.5)
  }, animation_duration, 'swing');

  setTimeout(function() { 
    // blink(true);
    $('#label').hide();
    $('#expression').hide();
    $('#expression').css('margin-left', 0);
  }, zoomed_in_pause_duration);
}

let blink = (val) => {
  if (blink_interval) clearInterval(blink_interval);
  if (val) {
    blink_interval = setInterval( function() { 
      if ($( '#expression').css('display') === 'none') 
        $( '#expression').show();
      else
        $( '#expression').hide();
    }, 700 / speed);
  }
};