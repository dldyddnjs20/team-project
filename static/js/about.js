$("'.button'+ (i + 1)").on("click", function (e) {
	e.preventDefault();//anchor이벤트의 기본동작을 막는다.
	var thisTarget = $(this).attr("href");
	$(window).scrollTop($(thisTarget).offset().top);
});

$(document).ready(function() {
	$(window).scroll(function() {
		if($(this).scrollTop() > 100) {
			$('.top').fadeIn();
		} else {
			$('.top').fadeOut();
		} });
	$('.top').click(function() {
		$('html, body').animation({scrollTop: 0}, 400);
		return false;
	});
});