@extends('common.layout')

@section('index')
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
    <link rel="stylesheet" href="{{ asset('/css/style.css') }}">
</head>

<body>
    <br><hr>
    <div class="link">
        <a href="member_input.php">新規課員登録</a> 会員情報の登録を行います<br>
        <a href="http://www.example.com/">会員情報変更・削除</a> 会員情報の変更、削除を行います<br>
        <a href="http://www.example.com/">商品検索</a> 購入する商品の検索を行います<br>
        <a href="http://www.example.com/">お買い物かご</a> 商品の注文を行います<br>
    </div>
</body>
@endsection
