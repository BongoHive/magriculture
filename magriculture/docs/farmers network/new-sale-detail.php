<?php include_once('header.php'); ?>

	<div class="content">

		<div class="breadcrumb"><a href="/home.php">Home</a> &gt; <a href="/farmers.php">Farmers</a> &gt; New Sale</div>
		
		<h2>New Tomato Sale</h2>
		
		<form class="standard" action="/new-sale-detail-error.php">
			<label for="form-quantity">Quantity</label>
			<input type="text" id="form-quantity" />

			<label for="form-quality">Quality</label>
			<select id="form-quality">
				<option>Excellent</option>
				<option>Average</option>
				<option>Poor</option>
			</select>
			
			<label for="form-unit">Unit</label>
			<select id="form-unit">
				<option>Box</option>
				<option>Crate</option>
				<option>Single</option>
			</select>
			
			<label for="form-unit-price">Unit Price (ZK)</label>
			<input type="text" id="unit-price" />
			
			<label for="form-day">Date</label>
			<select id="form-day">
				<option>11</option>
				<option>12</option>
				<option>13</option>
			</select>
			
			<select id="form-month">
				<option>Jan</option>
				<option>Feb</option>
				<option>Mar</option>
			</select>
			
			<select id="form-year">
				<option>2011</option>
				<option>2012</option>
			</select>
			
			<label for="form-hour">Time</label>
			<select id="form-hour">
				<option>11</option>
				<option>12</option>
				<option>13</option>
			</select>
			
			<select id="form-minute">
				<option>34</option>
				<option>35</option>
				<option>36</option>
			</select>
			
			<input type="submit" name="submit" class="submit" value="Register Sale &raquo;" />
			<input type="submit" name="cancel" class="submit" value="Cancel" />
			
		</form>		
		
		<h2>Menu</h2>
		<?php include_once('menu.php'); ?>		
	</div> <!-- /.content -->

<?php include_once('footer.php'); ?>