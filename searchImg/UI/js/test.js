class SearchUI {
    constructor() {
        this.$pictureSearchWindows = $('#pictureSearchWindows')
        this.$pictureSearchHeader = $('#pictureSearchHeader')
        this.$pictureSearchMain = $('#pictureSearchMain');
        this.$pictureSearchContainer = $('#pictureSearchContainer');
        this.$pictureSearchCanvasContainer = $('#pictureSearchCanvasContainer');
        this.$pictureSearchCanvas = $('#pictureSearchCanvas');
        this.windowW = $(document).width() - 2;
        this.canvasW = this.windowW - 6
        this.windowH = this.$pictureSearchWindows.outerHeight() - this.$pictureSearchHeader.outerHeight();
        this.canvasMaxH = 5000;

    }
    init() {
        this.setWindowSize();

    }
    setWindowSize() {
        this.$pictureSearchMain.css({ 'width': this.windowW, 'height': this.windowH });
        this.$pictureSearchCanvasContainer.css({ 'width': this.canvasW, 'height': this.windowH });
        this.$pictureSearchCanvas.attr({ 'width': this.canvasW, 'height': this.canvasMaxH });

    }
}


let main = function() {
    let searchUI = new SearchUI();
    searchUI.init();

}()