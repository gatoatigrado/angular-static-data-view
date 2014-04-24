app = angular.module("app", []);
function TopLevelController($scope, $http) {
    $scope.data = [];
    $http.get('data.json').success(function(data) {
        $scope.data = data;
    });
}
