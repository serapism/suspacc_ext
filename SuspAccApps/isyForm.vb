Public Class isyForm
    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        MsgBox("Hello World!")
        MsgBox(CheckBox1.CheckState)
    End Sub

    Private Sub ComboBox1_SelectedIndexChanged(sender As Object, e As EventArgs)
        MsgBox(ComboBox1.Text)

        'writea code to tell the age from date of birth
        Dim dob As Date = DateTimePicker1.Value
        Dim age As Integer = Date.Today.Year - dob.Year
        MsgBox(age)

    End Sub
End Class