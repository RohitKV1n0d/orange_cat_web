(function($){
"use strict";

	$(window).on( 'load', function(){
		/*--------------------- PRELOADER --------------------*/
		$('body').addClass('animated-page page-loaded');

		/*----------------------- WOW ------------------------*/
		if( $( '.wow' )[0] ){
			new WOW({
				mobile: false,
			}).init();
		}

		/* ----------------- SLIDER HOME ONE ---------------- */
		if($('.main-slider')[0]){
			$('.main-slider').slick({
				infinite: true,
				slidesToShow: 1,
				slidesToScroll: 1,
				dots: true,
				arrows: true,
				speed: 1000,
				fade: true,
				cssEase: 'ease-in-out',
				cssEase: 'cubic-bezier(0.7, 0, 0.3, 1)',
				touchThreshold: 100,
				nextArrow: '<span class="slick-arrow-next"><i class="fa fa-angle-down" aria-hidden="true"></i></span>',
				prevArrow: '<span class="slick-arrow-prev"><i class="fa fa-angle-up" aria-hidden="true"></i></span>',
				appendArrows: $('.main-slide-navigation'),
				appendDots: $('.main-slide-navigation'),
				// autoplay: true,
				// autoplaySpeed: 4500,
				responsive: [
				{
					breakpoint: 768,
					settings: {
						dots: false,
						arrows: false,
					}
				}
				]
			});
		}

		/* ----------------- SLIDER HOME TWO ---------------- */
		if($('.dark-slider')[0]){
			$('.dark-slider').slick({
				slidesToShow: 1,
				slidesToScroll: 1,
				dots: true,
				arrows: true,
				speed: 800,
				fade: true,
				cssEase: 'ease-in-out',
				cssEase: 'cubic-bezier(0.7, 0, 0.3, 1)',
				touchThreshold: 100,
				nextArrow: '<span class="slick-arrow-next"><i class="fa fa-angle-right" aria-hidden="true"></i></span>',
				prevArrow: '<span class="slick-arrow-prev"><i class="fa fa-angle-left" aria-hidden="true"></i></span>',
				appendArrows: $('.dark-slide-navigation'),
				appendDots: $('.dark-slide-navigation'),
				// autoplay: true,
				// autoplaySpeed: 4500,
				responsive: [
				{
					breakpoint: 768,
					settings: {
						dots: false,
						arrows: false,
					}
				}
				]
			});
		}
	});


	/* ----------------------- MENU ---------------------- */
	$( 'body' ).on('click', '.nav-btn',  function( event ){
		$( event.currentTarget ).toggleClass('active');
		$('.nav-menu').toggleClass('active');
		$( 'body' ).toggleClass('no-scroll');
		return false;
	});

	$( window ).on('resize.myTemplate', function(){
		$('body')[ ( $(this).width() <= 767 ) ? 'addClass' : 'removeClass' ]('isMobile')
	}).trigger( 'resize.myTemplate' );

	$( 'body' ).on('click', '.dropdown>a', function( event){
		if( ! $('body.isMobile')[0] ){
			return;
		}

		var $thisLi = $( event.currentTarget ).parents( 'li' ),
			$thisLiActive = $thisLi.hasClass( 'dropdown-active' );

		$('.dropdown-active').removeClass('dropdown-active').children('ul').slideUp('slow');

		if( ! $thisLiActive ){
			$thisLi.addClass('dropdown-active');
			$thisLi.children('ul').slideDown('slow');
		}

		return false;
	});

	$( 'body' ).on( 'mouseenter', '.dropdown', function(event){
		if( $('body.isMobile')[0] ){
			return;
		}

		var menuItem = $( event.currentTarget );

		if( menuItem[0].timeOutMenu ){
			clearTimeout( menuItem[0].timeOutMenu );
		}

		menuItem.addClass('active');
	}).on( 'mouseleave', '.dropdown', function( event ){
		if( $('body.isMobile')[0] ){
			return;
		}

		var menuItem = $( event.currentTarget );

		menuItem[0].timeOutMenu = setTimeout( function(){
			menuItem.removeClass('active');
		}, 500 );
	});

	/* ------------------- TO TOP ------------------ */
	$(window).on( 'scroll.myTemplat', scrollWindow).trigger( 'scroll.myTemplat' );

	function scrollWindow() {
		if ($(window).scrollTop() > 500) {
			$('.to-top').addClass('active');
		} else {
			$('.to-top').removeClass('active');
		}
	}

	$( 'body' ).on( 'click', '.to-top',  function(event) {
		$('html, body').animate({
			scrollTop:0
		}, 400);
		return false;
	});

	/*--------------- SCROLL ELLEMENTS	---------------*/
	if( $( '.item-scroll' )[0] ){
		$( 'body' ).on('click', '.item-scroll', function( event ){
			var scroll_el = $( event.currentTarget ).attr('href');

			if ($(scroll_el).length != 0) {
				$('html, body').animate({
					scrollTop: $(scroll_el).offset().top
				}, 500);
			}
			return false;
		});
	}

	/* ---------------- HEADER 2 SEARCH --------------- */
	if( $('.header-two-search')[0] ){
		$( 'body' ).on( 'click', '.header-search-icon', function( event ){
			$('.header-two-search').toggleClass('active');
		});

		$( document ).on( 'mouseup', function( event ){
			var divSearch = $('.header-two-search');

			if ( ! divSearch.is( event.target ) && divSearch.has( event.target ).length === 0) {
				divSearch.removeClass('active');
			}
		});
	}
	/* -------------------- ISOTOPE ------------------- */
	if( $( '.grid-gallery' )[0] ){
		var $grid = $('.grid-gallery').isotope({
			itemSelector: '.our-gallery-item',
			percentPosition: true,
			masonry: {
				columnWidth: '.grid-sizer'
			}
		});

		$( window ).on( 'load', rebuildMasonry ).on( 'resize', rebuildMasonry );
		function rebuildMasonry(){
			$grid.isotope();
		}
	}
	/* ------------------- FANCYBOX 3 ------------------ */
	if( $( '[data-fancybox]' )[0] ){
		$( '[data-fancybox]' ).fancybox({
			loop: true,
			infobar: false,
			transitionEffect: 'tube',
			buttons: [
			'close'
			],
		});
	}

	/*------------------- MODAL WINDOW	-------------------*/
	if($('.popup-open')[0]){
		$( 'body' ).on('click', '.popup-open', function( event ){
			var rel = $( event.currentTarget ).attr('rel');

			$('body').addClass('modal');
			$('.overlay').addClass('active');
			$('.popup').removeClass('active');
			$('.popup-'+rel).addClass('active');

			return false;
		});

		$( 'body' ).on('click', '.popup-close, .overlay', function(){
			$('body').removeClass('modal');
			$('.overlay').removeClass('active');
			$('.popup').removeClass('active');

			return false;
		});
	}

	/*------------------ PLAY/STOP VIDEO ------------------*/
	if($('.close_vid')[0]){

		$( 'body' ).on('click', '.close_vid', function() {
			$("iframe").each( function() {
				$( this )[0].contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*')
			});
		});

		$( 'body' ).on('click', '.play_video', function() {
			$("iframe").each( function() {
				$( this )[0].contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*')
			});
		});
	}

	/* -------------------- TAB SCHEDULE ------------------ */
	if($('.description-toggle')[0]){
		$( 'body' ).on('click', '.description-toggle > li > .title', function( event ){
			$('.description-toggle .description-toggle-info').not( $( event.currentTarget ).parents('li').find('.description-toggle-info')).hide('ease');
			$( event.currentTarget ).parents('li').find('.description-toggle-info').toggle('ease');
		});
	}
	/*-------------------- NICE SELECT --------------------*/
	if($('.nice-select')[0]){
		$('.nice-select').niceSelect();
	}

	/*------------------------ LAZY  -----------------------*/
	if( $( '.lazy' )[0] ){
		$('.lazy').Lazy({
			effect: "fadeIn",
			effectTime: 500,
			threshold: 500
		});
	}

	/* --------------- SLIDER-CATEG-BICYKLE -------------- */
	if( $('.slider-categ-bicycle')[0] ){
		$( '.slider-categ-bicycle' ).slick({
			slidesToShow: 3,
			slidesToScroll: 1,
			arrows: true,
			speed: 800,
			touchThreshold: 200,
			cssEase: 'cubic-bezier(0.7, 0, 0.3, 1)',
			nextArrow: '<span class="slick-arrow-next"><i class="fa fa-angle-right" aria-hidden="true"></i></span>',
			prevArrow: '<span class="slick-arrow-prev"><i class="fa fa-angle-left" aria-hidden="true"></i></span>',
			// autoplay: true,
			// autoplaySpeed: 4500,
			responsive: [
			{
				breakpoint: 1200,
				settings: {
					slidesToShow: 2,
				}
			},
			{
				breakpoint: 576,
				settings: {
					slidesToShow: 1,
				}
			}
			]
		});
	}

	/* -------------- SLIDER-CATEG-BICYKLE ------------- */
	if( $('.feedback-slider')[0] ){
		$( '.feedback-slider' ).slick({
			slidesToShow: 3,
			slidesToScroll: 1,
			arrows: true,
			speed: 800,
			touchThreshold: 200,
			cssEase: 'cubic-bezier(0.7, 0, 0.3, 1)',
			nextArrow: '<span class="slick-arrow-next"><i class="fa fa-angle-right" aria-hidden="true"></i></span>',
			prevArrow: '<span class="slick-arrow-prev"><i class="fa fa-angle-left" aria-hidden="true"></i></span>',
			// autoplay: true,
			// autoplaySpeed: 4500,
			responsive: [
			{
				breakpoint: 1200,
				settings: {
					slidesToShow: 2,
				}
			},
			{
				breakpoint: 576,
				settings: {
					slidesToShow: 1,
				}
			}
			]
		});
	}

	/* -------------- SLIDER-CATEG-BICYKLE ------------- */
	if( $('.clients-cover')[0] ){
		$( '.clients-cover' ).slick({
			infinite: true,
			slidesToShow: 5,
			slidesToScroll: 1,
			arrows: false,
			speed: 800,
			touchThreshold: 200,
			cssEase: 'cubic-bezier(0.7, 0, 0.3, 1)',
			autoplay: true,
			autoplaySpeed: 4500,
			responsive: [
			{
				breakpoint: 576,
				settings: {
					slidesToShow: 3,
					slidesToScroll: 3,
				}
			}
			]
		});
	}



	/*------------------------ TABS -----------------------*/
	if( $( '.tab-wrap' )[0] ){
		$( '.tab-wrap' )
		.on( 'click', '.tab-nav .item', switchTab )
		.find( '.tab-nav .item:first-child' ).trigger( 'click' );

		function switchTab( event ){
			var curentTab = $( this ),
			tabWrapper = $( event.delegateTarget ),
			visibleContent = $( '.' + curentTab.attr('rel') ),
			contentHeight;

			$( '.active', tabWrapper ).removeClass( 'active' );
			curentTab.addClass( 'active' );

			$( '.visible-content', tabWrapper ).removeClass( 'visible-content' );
			visibleContent.addClass( 'visible-content' );

			contentHeight = visibleContent.height();
			$( '.tabs-content', tabWrapper ).height( contentHeight );
		}

		$( window ).on( 'resize.myTemplate' , resizeTab );

		function resizeTab( event ){
			var visibleContent = $( '.tab.visible-content' );
			setTimeout(function(){
				visibleContent.each( function() {
					var contentHeight = $( this ).outerHeight(true),
							tabsContent = $( this ).parents( '.tabs-content' );

					tabsContent.height( contentHeight );
				} );
			}, 700);
		}

	}

	/*------------------------ COUNTDOWN -----------------------*/
	if( $( '#clockdiv' )[0] ){
		function getTimeRemaining(endtime) {
			var t = Date.parse(endtime) - Date.parse(new Date());
			var seconds = Math.floor((t / 1000) % 60);
			var minutes = Math.floor((t / 1000 / 60) % 60);
			var hours = Math.floor((t / (1000 * 60 * 60)) % 24);
			var days = Math.floor(t / (1000 * 60 * 60 * 24));
			return {
				'total': t,
				'days': days,
				'hours': hours,
				'minutes': minutes,
				'seconds': seconds
			};
		}

		function initializeClock(id, endtime) {
			var clock = document.getElementById(id);
			var daysSpan = clock.querySelector('.days');
			var hoursSpan = clock.querySelector('.hours');
			var minutesSpan = clock.querySelector('.minutes');
			var secondsSpan = clock.querySelector('.seconds');

			function updateClock() {
				var t = getTimeRemaining(endtime);

				daysSpan.innerHTML = t.days;
				hoursSpan.innerHTML = ('0' + t.hours).slice(-2);
				minutesSpan.innerHTML = ('0' + t.minutes).slice(-2);
				secondsSpan.innerHTML = ('0' + t.seconds).slice(-2);

				if (t.total <= 0) {
					clearInterval(timeinterval);
				}
			}

			updateClock();
			var timeinterval = setInterval(updateClock, 1000);
		}

		var deadline = new Date(Date.parse(new Date()) + 15 * 24 * 60 * 60 * 1000);
		initializeClock('clockdiv', deadline);
	}

	/* ----------------------- COUNTER ---------------------- */
	if ( $('.counter-animate.counter-active')[0] ) {
		$( window ).on( 'scroll', function(){
			var winScrollTop = $( this ).scrollTop(),
				windowHeight = $( this ).height();

			$('.counter-animate.counter-active').each(function(){
				var $this = $(this),
				targetPos = $this.offset().top;
				if( targetPos < winScrollTop + 100 + windowHeight / 2 ){
					if( $this.hasClass( 'counter-active' )){
						var time = 1;
						$('.about-count-item .number span').each(function(){
							var i = 1,
							num = $(this).data('number'),
							step = 5 * time / num,
							that = $(this),
							int = setInterval(function(){
								if (i <= num) {
									that.html(i);
								}
								else {
									clearInterval(int);
								}
								i++;
							},step);
						});
						$this.removeClass('counter-active');
					}
				}
			});
		});
	}
	/*--------------------- WIDGET RANGE ---------------------*/
	if( $( '#slider-range' )[0] ){
		$( "#slider-range" ).slider({
			range: true,
			min: 1,
			max: 5000,
			values: [ 1000, 4000 ],
			slide: function( event, ui ) {
				$( "#amount-min" ).val(ui.values[ 0 ]);
				$( "#amount-max" ).val( ui.values[ 1 ]);
			}
		});
		$( "#amount-min" ).val( $( "#slider-range" ).slider( "values", 0 ));
		$( "#amount-max" ).val( $( "#slider-range" ).slider( "values", 1 ));
	}
	/* -------------------- RESET FILTER -------------------- */
	if($('.reset-filter-btn' )[0]){
		$( 'body' ).on('click', '.reset-filter-btn', function(){
			$('.wigets-shop input').removeAttr('checked');
			return false;
		});
	}
	/* -------------------- CONTACT FORM -------------------- */
	if( $( '#contactform' )[0] ){
		$( 'body' ).on( 'submit', '#contactform', function() {
			var action = $( this ).attr( 'action' ),
				message = $( '#message' ),
				submit = $( '#submit' );

			message.slideUp( 750, function() {
				message.hide();
				submit.attr( 'disabled', 'disabled' );
				$.post(
					action,
					{
						name: $( '#name' ).val(),
						email: $( '#email' ).val(),
						phone: $( '#phone' ).val(),
						comments: $( '#comments' ).val(),
					},
					function( event ) {
						document.getElementById( 'message' ).innerHTML = event;
						message.slideDown( 'slow' );
						submit.removeAttr( 'disabled' );

						if ( null != event.match( 'success' ) ) {
							$( '#contactform' ).slideDown( 'slow' );
						}
					}
					);
			});
			return false;
		});
	}

	/*----------------- SORT PRODUCT SHOP -----------------*/
	$( 'body' ).on('click', '.sort-form li', function( event ){
		var sort = $( event.currentTarget ).attr('data-atr');
		$( '.sort-form li' ).removeClass('active');
		$( event.currentTarget ).addClass('active');
		$( '.shop-product-cover .product-cover' ).removeClass('large block list').addClass(sort);
	});

	$( 'body' ).on('click', '.shop-sidebar-btn, .btn-sidebar', function(){
		$('.shop-sidebar, .sidebar .widgets').toggle('ease');
		return false;
	});

	/* -------------- SLIDER SINGLE PRODUCT ------------- */
	if( $( '.slider-single-for' )[0] ){
		$( '.slider-single-for' ).slick({
			slidesToShow: 1,
			slidesToScroll: 1,
			dots: false,
			arrows: false,
			fade: true,
			speed: 600,
			cssEase: 'ease-in-out',
			asNavFor: '.slider-single-nav'
		});
		$( '.slider-single-nav' ).slick({
			slidesToShow: 4,
			slidesToScroll: 1,
			dots: false,
			arrows: false,
			asNavFor: '.slider-single-for',
			cssEase: 'ease-in-out',
			focusOnSelect: true,
			infinite: true,
			speed: 600,
		});
	}

	/* --------------------- QUANITY ------------------- */
	if( $( '#quanity' )[0] ){
		$( "#quanity" ).spinner({
			max: 1000,
			min: 1
		});
	}

	/* ----------------- SINGLE SHOP SIZE -------------- */
	if( $( '.wheel-size' )[0] ){
		$( 'body' ).on('click', '.wheel-size li', function( event ){
			$('.wheel-size li').removeClass('active');
			$( event.currentTarget ).addClass('active');
		});
	}
	if( $( '.frame-size' )[0] ){
		$( 'body' ).on('click', '.frame-size li', function( event ){
			$('.frame-size li').removeClass('active');
			$( event.currentTarget ).addClass('active');
		});
	}

	/* -------------------- GOOGLE MAP ------------------ */
	if( $( '.google-map' )[0] ){
		googleMapsInit();

		function googleMapsInit() {
			var mapOptions = {
				zoom: 11,
				center: new google.maps.LatLng(40.6501038, -73.9495823),
				mapTypeControl: false,
				fullscreenControl: false,
				scalecontrol: false,
				zoomControl: false,
				streetViewControl: false,
				rotateControl: false,
				styles: [{'featureType':'all','elementType':'labels.text.fill','stylers':[{'saturation':36},{'color':'#000000'},{'lightness':40}]},{'featureType':'all','elementType':'labels.text.stroke','stylers':[{'visibility':'on'},{'color':'#000000'},{'lightness':16}]},{'featureType':'all','elementType':'labels.icon','stylers':[{'visibility':'off'}]},{'featureType':'administrative','elementType':'geometry.fill','stylers':[{'color':'#000000'},{'lightness':20}]},{'featureType':'administrative','elementType':'geometry.stroke','stylers':[{'color':'#000000'},{'lightness':17},{'weight':1.2}]},{'featureType':'landscape','elementType':'geometry','stylers':[{'color':'#000000'},{'lightness':20}]},{'featureType':'poi','elementType':'geometry','stylers':[{'color':'#000000'},{'lightness':21}]},{'featureType':'road.highway','elementType':'geometry.fill','stylers':[{'color':'#000000'},{'lightness':17}]},{'featureType':'road.highway','elementType':'geometry.stroke','stylers':[{'color':'#000000'},{'lightness':29},{'weight':0.2}]},{'featureType':'road.arterial','elementType':'geometry','stylers':[{'color':'#000000'},{'lightness':18}]},{'featureType':'road.local','elementType':'geometry','stylers':[{'color':'#000000'},{'lightness':16}]},{'featureType':'transit','elementType':'geometry','stylers':[{'color':'#000000'},{'lightness':19}]},{'featureType':'water','elementType':'geometry','stylers':[{'color':'#000000'},{'lightness':17}]}]
			},
			mapElement = document.getElementById( 'map' ),
			map = new google.maps.Map( mapElement, mapOptions ),
			marker = new google.maps.Marker( {
				position: new google.maps.LatLng( 40.6401038, -73.9495823 ),
				map: map,
				icon: 'assets/img/icon-map.png'
			});
		}
	}
}(jQuery));





$(document).ready( function() {

					var itemSelector_1 = '.gallery-item'; 

					var $container1 = $('.gallery-row');
					$container1.imagesLoaded(function() {
						$container1.isotope({
							itemSelector : itemSelector_1,
							masonry : {
								horizontalOrder : true
							}
						});
					});

					//Ascending order
					var responsiveIsotope = [
						[480, 4],
						[720, 6]
					];

					var itemsPerPageDefault = 3;
					//var itemsPerPage = defineItemsPerPage();
					var itemsPerPage = 3;
					var currentNumberPages = 1;
					var currentPage = 1;
					var startPage=1;
					var currentFilter = '*';
					var filterAtribute = 'data-filter';
					var pageAtribute = 'data-page';
					var pagerClass = 'isotope-pager';

					function changeFilter(selector) {
						$container1.isotope({
							filter: selector
						});
					}


					function goToPage(n) {
						currentPage = n;

						var selector = itemSelector_1;
							//selector += ( currentFilter != '*' ) ? '['+filterAtribute+'="'+currentFilter+'"]' : '';
							selector += '['+pageAtribute+'="'+currentPage+'"]';
						changeFilter(selector);
					}

								
					function setPagination() {

						var SettingsPagesOnItems = function(){

							var itemsLength = $container1.children(itemSelector_1).length;
							
							var pages = Math.ceil(itemsLength / itemsPerPage);
							var item = 1;
							var page = 1;
							var selector = itemSelector_1;
								selector += ( currentFilter != '*' ) ? '['+filterAtribute+'="'+currentFilter+'"]' : '';
							
							$container1.children(selector).each(function(){
								if( item > itemsPerPage ) {
									page++;
									item = 1;
								}
								$(this).attr(pageAtribute, page);
								item++;
							});

							currentNumberPages = page;

						}();

						var CreatePagers = function() {

							var $isotopePager = ( $('.'+pagerClass).length == 0 ) ? $('<div class="'+pagerClass+' text-center"></div>') : $('.'+pagerClass);

							$isotopePager.html('');
							
							
							var $page_prev_btn=$('<a type="button" class="btn btn-primary previous_btn">Previous</a>');

								          
								          
							var $page_next_btn=$('<a type="button" class="btn btn-primary next_btn">Next</a>');
							$page_prev_btn.appendTo($isotopePager);
							
							for( var i = 0; i < currentNumberPages; i++ ) {
								var $pager = $('<a href="javascript:void(0);" class="pager" '+pageAtribute+'="'+(i+1)+'"></a>');
									$pager.html(i+1);
									
									$pager.click(function(){
										var page = $(this).eq(0).attr(pageAtribute);
										$('.isotope-pager a').removeClass("active");
										$(this).addClass("active");
										goToPage(page);
									});

								$pager.appendTo($isotopePager);
								$isotopePager.find('a.pager:first').addClass('active');
							}
							
							$page_next_btn.appendTo($isotopePager)
							$container1.after($isotopePager);

							$page_prev_btn.click(function(){
								if( currentPage > startPage)
					        	  {
					        	  	 $('.previous_btn').removeAttr('disabled');
					        	  	var page=  currentPage - 1;
						        	var page=currentPage - 1 < startPage
							          ? startPage
									          : currentPage - 1;
						        	$('.isotope-pager a').removeClass("active");
						        	$('.pager[data-page="'+page+'"]').addClass('active');
										goToPage(page);
					        	
					        	  }
								else {
									$('.previous_btn').attr('disabled','disabled');
									}

								
								});
							$page_next_btn.click(function(){
								 if( currentPage < currentNumberPages)
					        	  {
					        	  	 $('.next_btn').removeAttr('disabled');
					        	  	var page=currentPage + 1 > currentNumberPages
							          ? currentNumberPages
									          : currentPage + 1;
						        	$('.isotope-pager a').removeClass("active");
						        	$('.pager[data-page="'+page+'"]').addClass('active');
										goToPage(page);
					        	  	}
					        	  else {
					        	  	$('.next_btn').attr('disabled','disabled');
					        	  }
									});

						}();

					}

					setPagination();
					goToPage(1);

					

				});


// ------------------faq-------------------
  //<![CDATA[
	let toggles = document.getElementsByClassName("toggle");
	let contentDiv = document.getElementsByClassName("content-faq");
	let icons = document.getElementsByClassName("icon");

	for (let i = 0; i < toggles.length; i++) {
		toggles[i].addEventListener("click", () => {
			if (parseInt(contentDiv[i].style.height) != contentDiv[i].scrollHeight) {
				contentDiv[i].style.height = contentDiv[i].scrollHeight + "px";
				toggles[i].style.color = "#F45F30";
				icons[i].classList.remove("fa-plus");
				icons[i].classList.add("fa-minus");
			} else {
				contentDiv[i].style.height = "0px";
				toggles[i].style.color = "#F45F30";
				icons[i].classList.remove("fa-minus");
				icons[i].classList.add("fa-plus");
			}

			for (let j = 0; j < contentDiv.length; j++) {
				if (j !== i) {
					contentDiv[j].style.height = 0;
					toggles[j].style.color = "#111130";
					icons[j].classList.remove("fa-minus");
					icons[j].classList.add("fa-plus");
				}
			}
		});
	}
//]]>

				